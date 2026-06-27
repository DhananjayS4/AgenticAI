import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/agents')))

from security import SecurityManager
from database import DatabaseManager
from sanitizer import SanitizerAgent
from coordinator import CoordinatorAgent

def test_sanitized_pipeline():
    print("Testing Sanitizer and Coordinator Agent pipeline...")
    
    db_path = "test_agent_vault.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize managers and agents
    db = DatabaseManager(db_path=db_path, passphrase="agent-test-password")
    sanitizer = SanitizerAgent()
    coordinator = CoordinatorAgent(db)

    # User input containing PII
    raw_prompt = 'Add contact "Alice Smith" phone "555-123-4567" email "alice.smith@example.com" notes "Met her in Paris"'
    print(f"Original user prompt: {raw_prompt}")

    # Step 1: Sanitize user input
    sanitized_prompt, mapping = sanitizer.sanitize(raw_prompt)
    print(f"Sanitized user prompt: {sanitized_prompt}")
    print(f"Sanitizer Mapping: {mapping}")

    # Check that redaction occurred
    assert "[REDACTED_PHONE_1]" in sanitized_prompt
    assert "[REDACTED_EMAIL_1]" in sanitized_prompt
    assert "555-123-4567" not in sanitized_prompt
    assert "alice.smith@example.com" not in sanitized_prompt

    # Step 2: Run coordinator with sanitized prompt and mapping
    result = coordinator.run(sanitized_prompt, mapping)
    print(f"Agent Action Executed: {result['action']}")
    print(f"Agent Thoughts: {result['thoughts']}")
    print(f"Agent Response: {result['response']}")

    # Step 3: Verify DB contains the desanitized original values (stored in encrypted format)
    contacts = db.get_all_contacts()
    assert len(contacts) == 1, "Should have saved 1 contact"
    contact = contacts[0]
    
    print(f"Decrypted contact read from DB: Name: {contact['name']}, Phone: {contact['phone']}, Email: {contact['email']}")
    assert contact["name"] == "Alice Smith"
    assert contact["phone"] == "555-123-4567", f"Expected '555-123-4567', got {contact['phone']}"
    assert contact["email"] == "alice.smith@example.com", f"Expected 'alice.smith@example.com', got {contact['email']}"
    
    # Check sanitizer logs
    logs = sanitizer.get_logs()
    print("Sanitizer logs:")
    for log in logs:
        print(f" - {log}")
    assert len(logs) >= 2, "Should have at least 2 logs (phone and email)"

    # Clean up
    db.conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    print("Agent pipeline tests completed successfully!")

if __name__ == "__main__":
    try:
        test_sanitized_pipeline()
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
