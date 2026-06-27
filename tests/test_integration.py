import os
import sys
import time
import json
import asyncio
import subprocess
import requests

async def test_websocket_interaction():
    print("Connecting to secure WebSocket endpoint...")
    import websockets
    
    uri = "ws://127.0.0.1:8000/ws/chat"
    async with websockets.connect(uri) as ws:
        # Step 1: Send passphrase unlock request
        print("Sending vault unlock credentials...")
        await ws.send(json.dumps({"passphrase": "integration-test-passphrase"}))
        
        # Read initialization message
        init_res = await ws.recv()
        init_data = json.loads(init_res)
        print(f"Server response: {init_data}")
        assert init_data["type"] == "system"
        assert "Vault unlocked" in init_data["message"]
        
        # Step 2: Send prompt containing PII
        pii_prompt = "My credit card number is 4111-2222-3333-4444 and my phone is 555-987-6543. Add a task 'Buy flowers for mom'."
        print(f"\nSending prompt with PII: '{pii_prompt}'")
        await ws.send(json.dumps({"prompt": pii_prompt}))
        
        # Step 3: Stream and verify events
        has_redaction = False
        has_thoughts = False
        has_response = False
        
        while True:
            try:
                # Wait for messages with a timeout
                msg_str = await asyncio.wait_for(ws.recv(), timeout=10.0)
                msg = json.loads(msg_str)
                print(f"Streamed Event -> Type: {msg['type']}, Data: {msg.get('message', '')}")
                
                if msg["type"] == "security_alert":
                    has_redaction = True
                    # Assert credit card and phone are masked
                    assert "[REDACTED_CREDIT_CARD_1]" in msg["message"] or "[REDACTED_PHONE_1]" in msg["message"]
                
                elif msg["type"] == "thought":
                    has_thoughts = True
                    
                elif msg["type"] == "response":
                    has_response = True
                    assert "Added" in msg["message"] or "task" in msg["message"]
                    # End loop when response is received
                    break
                    
            except asyncio.TimeoutError:
                print("WebSocket timeout waiting for response.")
                break
                
        assert has_redaction, "Sanitizer Agent failed to redact credit card number!"
        assert has_thoughts, "Coordinator Agent failed to stream thoughts!"
        assert has_response, "Coordinator Agent failed to yield a final response!"
        print("\nWebSocket communication flow verified successfully.")

def run_integration_test():
    print("=== STARTING FULL SYSTEM INTEGRATION TEST ===")
    
    # 1. Start uvicorn server in subprocess
    print("Starting FastAPI backend server...")
    env = os.environ.copy()
    # Force default DB path for tests to avoid cluttering local DB
    server_proc = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Allow uvicorn to bind
    time.sleep(3.0)
    
    try:
        # 2. Check health endpoint
        print("Checking API health status...")
        res = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
        assert res.status_code == 200, "Health check failed!"
        print(f"Health response: {res.json()}")
        
        # 3. Run async websocket tests
        asyncio.run(test_websocket_interaction())
        
        # 4. Check vault stats API
        print("\nChecking secure stats API...")
        res = requests.get("http://127.0.0.1:8000/api/vault/stats?passphrase=integration-test-passphrase", timeout=5)
        assert res.status_code == 200
        stats = res.json()
        print(f"Vault statistics: {stats}")
        assert stats["tasks_count"] > 0, "Task was not saved to SQLite!"
        
        print("\nAll integration tests passed successfully!")
        
    finally:
        # Shutdown server process
        print("Stopping backend server...")
        server_proc.terminate()
        server_proc.wait()
        
        # Clean up database file
        db_path = "backend/vault.db"
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print("Temporary test vault database cleaned up.")
            except Exception as e:
                print(f"Warning: could not delete database: {e}")

if __name__ == "__main__":
    try:
        run_integration_test()
    except AssertionError as e:
        print(f"\nIntegration Test Assertion Failure: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nIntegration Test Error: {e}")
        sys.exit(1)
