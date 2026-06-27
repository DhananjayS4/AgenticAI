import os
import json
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import DatabaseManager
from agents.sanitizer import SanitizerAgent
from agents.coordinator import CoordinatorAgent

app = FastAPI(title="Guardian - Privacy-First Concierge API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global list to store session security logs
security_alerts = []

class ConfigSchema(BaseModel):
    passphrase: str = "guardian-default-passphrase"

def get_db(passphrase: str = "guardian-default-passphrase"):
    return DatabaseManager(passphrase=passphrase)

@app.get("/api/health")
def health():
    return {"status": "online", "system": "Guardian Secure Core"}

@app.get("/api/vault/stats")
def get_stats(passphrase: str = "guardian-default-passphrase"):
    """Exposes record counts for each table to update the dashboard vault visualizer."""
    try:
        db = get_db(passphrase)
        notes = db.get_all_notes()
        tasks = db.get_all_tasks()
        contacts = db.get_all_contacts()
        db.conn.close()
        
        # Calculate statistics
        pending_tasks = sum(1 for t in tasks if t["status"] == "pending")
        completed_tasks = sum(1 for t in tasks if t["status"] == "completed")
        
        return {
            "notes_count": len(notes),
            "tasks_count": len(tasks),
            "pending_tasks_count": pending_tasks,
            "completed_tasks_count": completed_tasks,
            "contacts_count": len(contacts),
            "db_size_bytes": os.path.getsize(db.db_path) if os.path.exists(db.db_path) else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security/logs")
def get_security_logs():
    return {"logs": security_alerts}

@app.post("/api/security/logs/clear")
def clear_security_logs():
    global security_alerts
    security_alerts = []
    return {"status": "cleared"}

@app.get("/api/vault/data")
def get_vault_data(passphrase: str = "guardian-default-passphrase"):
    """Returns decrypted raw records to display inside the dashboard tabs."""
    try:
        db = get_db(passphrase)
        notes = db.get_all_notes()
        tasks = db.get_all_tasks()
        contacts = db.get_all_contacts()
        db.conn.close()
        return {
            "notes": notes,
            "tasks": tasks,
            "contacts": contacts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global security_alerts
    
    try:
        # Expect passphrase in the first message or default
        init_message = await websocket.receive_text()
        init_data = json.loads(init_message)
        passphrase = init_data.get("passphrase", "guardian-default-passphrase")
        
        db = get_db(passphrase)
        sanitizer = SanitizerAgent()
        coordinator = CoordinatorAgent(db)
        
        # Send confirmation connection state
        await websocket.send_json({
            "type": "system",
            "message": "Secure connection established. Vault unlocked."
        })
        
        while True:
            # Receive prompt from user
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            user_prompt = data.get("prompt", "")
            
            if not user_prompt:
                continue

            # Stream step 1: Sanitizer running
            await websocket.send_json({
                "type": "status",
                "message": "Security Guard scanning prompt for sensitive elements..."
            })
            await asyncio.sleep(0.4)
            
            sanitized_prompt, mapping = sanitizer.sanitize(user_prompt)
            
            # Stream sanitizer alerts if any PII was detected
            new_logs = sanitizer.get_logs()
            if new_logs:
                for log in new_logs:
                    security_alerts.append(log)
                    await websocket.send_json({
                        "type": "security_alert",
                        "message": log
                    })
                    await asyncio.sleep(0.3)
                sanitizer.clear_logs()
            else:
                await websocket.send_json({
                    "type": "status",
                    "message": "No unmasked PII elements detected in prompt."
                })
                await asyncio.sleep(0.2)

            # Stream step 2: Coordinator agent executing
            await websocket.send_json({
                "type": "status",
                "message": "Guardian Coordinator initiating intent parsing..."
            })
            await asyncio.sleep(0.4)
            
            # Execute coordinator logic
            result = coordinator.run(sanitized_prompt, mapping)
            
            # Stream chain of thought steps one-by-one to create a live, agentic visual effect
            for thought in result["thoughts"]:
                await websocket.send_json({
                    "type": "thought",
                    "message": thought
                })
                await asyncio.sleep(0.6)  # Paced for premium vibe aesthetics

            # Send final tool action log
            await websocket.send_json({
                "type": "action",
                "message": f"Executed local secure tool: {result['action']}"
            })
            await asyncio.sleep(0.3)

            # Send final response
            await websocket.send_json({
                "type": "response",
                "message": result["response"]
            })
            
            # Signal DB update so frontend fetches refreshed counts/vault lists
            await websocket.send_json({
                "type": "db_update"
            })
            
    except WebSocketDisconnect:
        print("Secure socket disconnected.")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"System error: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            db.conn.close()
        except:
            pass

# Mount frontend static files to serve the premium dashboard
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Read environment port for cloud deployment compatibility
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
