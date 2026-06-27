import sys
import json
import os

# Add parent directory to path so we can import the database manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import DatabaseManager

class SecureDBMcpServer:
    def __init__(self):
        # Use default passphrase for the local vault
        self.db = DatabaseManager(db_path=os.path.join(os.path.dirname(__file__), "../backend/vault.db"))
        self.tools = [
            {
                "name": "query_secure_vault",
                "description": "Perform an in-memory decrypted search across all notes in the secure SQLite vault database.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The keyword or text string to search for within decrypted notes."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "add_vault_note",
                "description": "Encrypts and stores a new note in the secure SQLite database.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the note."
                        },
                        "content": {
                            "type": "string",
                            "description": "Main text body content of the note."
                        }
                    },
                    "required": ["title", "content"]
                }
            }
        ]

    def serve(self):
        """Read JSON-RPC messages line by line from stdin, handle them, and write response to stdout."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                # Log error silently to stderr so stdout remains clean JSON-RPC
                sys.stderr.write(f"MCP Error: {str(e)}\n")
                sys.stderr.flush()

    def handle_request(self, req: dict) -> dict:
        method = req.get("method")
        req_id = req.get("id")
        
        # JSON-RPC response boilerplate
        res = {"jsonrpc": "2.0", "id": req_id}

        if method == "initialize":
            res["result"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "guardian-secure-db-mcp",
                    "version": "1.0.0"
                }
            }
            return res
            
        elif method == "tools/list":
            res["result"] = {
                "tools": self.tools
            }
            return res
            
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                content = self.execute_tool(name, arguments)
                res["result"] = {
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                }
            except Exception as e:
                res["error"] = {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            return res
            
        # Ignore other protocols or send method not found
        res["error"] = {
            "code": -32601,
            "message": f"Method {method} not found"
        }
        return res

    def execute_tool(self, name: str, args: dict) -> str:
        if name == "query_secure_vault":
            query = args.get("query", "")
            results = self.db.search_notes(query)
            if not results:
                return f"No records matching '{query}' found in the encrypted vault."
            
            output = f"Decrypted Search Results for '{query}':\n"
            for n in results:
                output += f"- Note #{n['id']}: [{n['title']}] (Created: {n['created_at']})\n  Content: {n['content']}\n"
            return output
            
        elif name == "add_vault_note":
            title = args.get("title", "")
            content = args.get("content", "")
            note_id = self.db.add_note(title, content)
            return f"Success: Encrypted note '{title}' saved with ID {note_id}."
            
        else:
            raise ValueError(f"Unknown tool name: {name}")

if __name__ == "__main__":
    server = SecureDBMcpServer()
    server.serve()
