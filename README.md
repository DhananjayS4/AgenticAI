# Guardian: Privacy-First Concierge & Data Vault

Guardian is a local-first, privacy-minded concierge agent system built to manage sensitive personal data (notes, tasks, and contacts) securely. All data stored in SQLite is encrypted client-side/locally via **AES-256-GCM** using keys derived from a user passphrase. 

A dedicated **Security Sanitizer Agent** intercepts inputs, redacting sensitive PII (emails, phone numbers, credentials) before they are sent to external LLMs, swapping them back on the local side.

---

## 🌟 Key Features
- **Client-Side Encrypted SQLite Vault**: Your diary, passwords, and contacts are encrypted with AES-256-GCM in-memory. The raw SQLite file contains only ciphertext.
- **Security Sanitizer Agent**: Intercepts queries, runs regex patterns for PII detection, redacts data, and unmasks responses locally.
- **WebSocket Thoughts Streaming**: Displays the agent's chain-of-thought, action logs, and redaction warnings step-by-step with real-time CSS animations.
- **Custom MCP Server**: Direct support for the Model Context Protocol to query or write records securely using standard JSON-RPC tools.
- **Single-Service Deployability**: FastAPI serves the premium dashboard UI, the WebSockets telemetry channel, and the vault API simultaneously.

---

## 🛠️ Implemented Course Concepts
Guardian implements four core course concepts:
1. **Agent & Multi-Agent System (ADK)**: Features a Coordinator Agent and a Sanitizer Agent running in a structured pipeline.
2. **MCP Server**: Implements a stdin/stdout JSON-RPC server with `query_secure_vault` and `add_vault_note` tools.
3. **Security Features**: In-memory AES-GCM database encryption and PII data scrubbing.
4. **Deployability**: Unified single-container architecture pre-configured for Docker Compose and free hosting platforms like Render.

---

## 🚀 Quick Start (Local Setup)

### Option 1: Python Native (Recommended)
1. **Clone the repository** (or open the workspace directory).
2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Set your environment** (Optional: add a `GEMINI_API_KEY` to `.env` to enable advanced conversation logic):
   ```bash
   # Create a .env file inside backend/
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. **Run the server**:
   ```bash
   python backend/main.py
   ```
5. **Access the app**: Open `http://localhost:8000` in your web browser.

---

### Option 2: Docker Compose
Run the entire application in a sandboxed container:
```bash
docker-compose up --build
```
Open `http://localhost:8000` in your browser.

---

## ☁️ Cloud Deployment (Free Hosting)
Guardian is designed as a single service, making it compatible with free-tier providers:

### Render Deployment (Backend & Frontend)
1. Push this codebase to a public GitHub repository.
2. Log in to [Render](https://render.com/) and create a new **Web Service**.
3. Link your GitHub repository.
4. Use the following configuration:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python backend/main.py`
5. Render will build and serve your app. Visited the generated `.onrender.com` URL to view the premium dashboard.

---

## 🤖 Console Commands Cheat Sheet
Interact with Guardian by typing commands in the console:

### 📄 Notes
- **Add Note**: `add note titled "Shopping List" with content "Milk, bread, and chocolate"`
- **List Notes**: `show all notes` or `list notes`
- **Search Notes**: `search notes for "chocolate"`
- **Delete Note**: `delete note <id>`

### ⬜ Tasks
- **Add Task**: `add task "Submit Capstone Project" due "2026-07-06"`
- **List Tasks**: `show tasks`
- **Complete Task**: `complete task <id>` (or click the checkbox in the UI)
- **Delete Task**: `delete task <id>`

### 👤 Contacts
- **Add Contact**: `add contact "Alice" phone "555-0199" email "alice@gmail.com" notes "Project coworker"`
- **List Contacts**: `show contacts`
- **Delete Contact**: `delete contact <id>`
