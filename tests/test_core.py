import sys
import os
import shutil

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from security import SecurityManager
from database import DatabaseManager

def test_encryption():
    print("Testing Encryption/Decryption...")
    sec = SecurityManager(passphrase="my-secret-passphrase", salt_str="my-salt")
    original = "Hello World! This is a sensitive record containing credentials: password123."
    ciphertext = sec.encrypt(original)
    assert ciphertext != original, "Ciphertext should not match original plaintext"
    
    decrypted = sec.decrypt(ciphertext)
    assert decrypted == original, f"Expected '{original}', but got '{decrypted}'"
    print("Encryption/Decryption passed successfully.")

def test_database():
    print("\nTesting SQLite Database Manager (with encryption)...")
    db_path = "test_vault.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = DatabaseManager(db_path=db_path, passphrase="test-password")

    # Test Notes
    print("Inserting notes...")
    n1 = db.add_note("Secret Diary", "Today I wrote some vibe coding code.")
    n2 = db.add_note("Server Credentials", "The API key is gemini-abc-123")
    
    all_notes = db.get_all_notes()
    assert len(all_notes) == 2, f"Expected 2 notes, got {len(all_notes)}"
    
    # Verify titles and contents are correctly decrypted
    diary = [n for n in all_notes if n["id"] == n1][0]
    assert diary["title"] == "Secret Diary"
    assert diary["content"] == "Today I wrote some vibe coding code."
    
    # Test search
    print("Searching notes...")
    results = db.search_notes("gemini")
    assert len(results) == 1, f"Expected 1 search result, got {len(results)}"
    assert results[0]["title"] == "Server Credentials"

    # Test Tasks
    print("Testing tasks...")
    t1 = db.add_task("Finish Capstone Writeup", "2026-07-06")
    all_tasks = db.get_all_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0]["title"] == "Finish Capstone Writeup"
    
    db.update_task_status(t1, "completed")
    all_tasks = db.get_all_tasks()
    assert all_tasks[0]["status"] == "completed"

    # Test Contacts
    print("Testing contacts...")
    c1 = db.add_contact("John Doe", "+123456789", "john@example.com", "Met at Kaggle meetups")
    all_contacts = db.get_all_contacts()
    assert len(all_contacts) == 1
    assert all_contacts[0]["name"] == "John Doe"
    assert all_contacts[0]["phone"] == "+123456789"
    assert all_contacts[0]["email"] == "john@example.com"
    
    # Clean up test DB
    db.conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    print("Database testing passed successfully.")

if __name__ == "__main__":
    try:
        test_encryption()
        test_database()
        print("\nAll tests passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
