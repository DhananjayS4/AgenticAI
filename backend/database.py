import sqlite3
import datetime
from security import SecurityManager

class DatabaseManager:
    def __init__(self, db_path="vault.db", passphrase="guardian-default-passphrase"):
        self.db_path = db_path
        self.security = SecurityManager(passphrase=passphrase)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        ''')
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    # Notes Operations
    def add_note(self, title: str, content: str) -> int:
        enc_title = self.security.encrypt(title)
        enc_content = self.security.encrypt(content)
        created_at = datetime.datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
            (enc_title, enc_content, created_at)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_note(self, note_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, content, created_at FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "title": self.security.decrypt(row[1]),
            "content": self.security.decrypt(row[2]),
            "created_at": row[3]
        }

    def get_all_notes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
        rows = cursor.fetchall()
        notes = []
        for row in rows:
            notes.append({
                "id": row[0],
                "title": self.security.decrypt(row[1]),
                "content": self.security.decrypt(row[2]),
                "created_at": row[3]
            })
        return notes

    def search_notes(self, query: str):
        query = query.lower()
        notes = self.get_all_notes()
        return [n for n in notes if query in n["title"].lower() or query in n["content"].lower()]

    def delete_note(self, note_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Tasks Operations
    def add_task(self, title: str, due_date: str = "", status: str = "pending") -> int:
        enc_title = self.security.encrypt(title)
        created_at = datetime.datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, due_date, status, created_at) VALUES (?, ?, ?, ?)",
            (enc_title, due_date, status, created_at)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, due_date, status, created_at FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "title": self.security.decrypt(row[1]),
                "due_date": row[2],
                "status": row[3],
                "created_at": row[4]
            })
        return tasks

    def update_task_status(self, task_id: int, status: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Contacts Operations
    def add_contact(self, name: str, phone: str = "", email: str = "", notes: str = "") -> int:
        enc_name = self.security.encrypt(name)
        enc_phone = self.security.encrypt(phone) if phone else ""
        enc_email = self.security.encrypt(email) if email else ""
        enc_notes = self.security.encrypt(notes) if notes else ""
        created_at = datetime.datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, phone, email, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            (enc_name, enc_phone, enc_email, enc_notes, created_at)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_contacts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, phone, email, notes, created_at FROM contacts ORDER BY name ASC")
        rows = cursor.fetchall()
        contacts = []
        for row in rows:
            contacts.append({
                "id": row[0],
                "name": self.security.decrypt(row[1]),
                "phone": self.security.decrypt(row[2]) if row[2] else "",
                "email": self.security.decrypt(row[3]) if row[3] else "",
                "notes": self.security.decrypt(row[4]) if row[4] else "",
                "created_at": row[5]
            })
        return contacts

    def search_contacts(self, query: str):
        query = query.lower()
        contacts = self.get_all_contacts()
        return [
            c for c in contacts 
            if query in c["name"].lower() or query in c["email"].lower() or query in c["notes"].lower()
        ]

    def delete_contact(self, contact_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()
        return cursor.rowcount > 0
