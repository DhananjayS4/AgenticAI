# Guardian: Video Demonstration Script
**YouTube Storyboard & Voiceover Script (Paced for Under 5 Minutes)**

---

## 🎬 Act 1: The Privacy Dilemma (0:00 - 0:45)

* **Visual**: Camera on host or high-quality title card with "GUARDIAN: Privacy-First AI Agent". Zoom into a database viewer showing a plain text note containing a server password.
* **Audio/Voiceover**: 
  > "AI agents are transforming how we work. But to be useful, they need access to our most private information: passwords, calendar events, personal emails, and contacts.
  > 
  > Typically, when you prompt a cloud-based agent, this sensitive data is transmitted in plain text directly to external LLM servers. If your database is compromised or device is stolen, your information is wide open.
  > 
  > Meet **Guardian**—a zero-trust, local-first concierge assistant that encrypts your database on disk using AES-256-GCM and redacts all PII before it ever leaves your machine."

---

## 🎬 Act 2: Technical Architecture & Flow (0:45 - 1:45)

* **Visual**: Present a clean, animated Mermaid diagram showing the flow (User Prompt -> Sanitizer Agent [redacting email/phone] -> Coordinator Agent -> Local Security Manager -> Encrypted SQLite Database).
* **Audio/Voiceover**:
  > "Guardian uses a multi-agent pipeline designed to separate private data from cloud reasoning.
  > 
  > First, the **Sanitizer Agent** intercepts your prompt. It scans for emails, phone numbers, and credentials, redacting them in-memory and replacing them with unique secure tokens.
  > 
  > Next, the **Coordinator Agent** processes the sanitized prompt, parsing your intent and calling local database tools. 
  > 
  > Finally, the **Security Manager** derives an encryption key from your passphrase using PBKDF2. It encrypts the original data using AES-256-GCM in-memory before saving it to your local SQLite database. The external LLM only ever sees masked tokens, while your local vault remains fully encrypted."

---

## 🎬 Act 3: Live Dashboard Demonstration (1:45 - 3:15)

* **Visual**: Screen recording of the premium glassmorphic dashboard in action:
  1. Shows the "Vault Locked" indicator.
  2. Host enters `guardian-default-passphrase` and clicks **Unlock**. Status changes to "Vault Unlocked" with a glowing emerald pulse. The stats cards update.
  3. Host types: `Add contact "Alice Peterson" phone "555-404-3322" email "alice@peterson.com"`.
  4. Point to the **Security Guard** panel in the right column. It lists:
     - `Redacted email 'ali...com' to [REDACTED_EMAIL_1]`
     - `Redacted phone '555...322' to [REDACTED_PHONE_1]`
  5. Show the **Concierge Console** chat feed streaming thoughts:
     - *Analyzing user input...*
     - *Intent identified: ADD_CONTACT...*
     - *Encrypting parameters...*
     - *Saved with ID 1.*
  6. Switch to the **Contacts** tab in the middle column. Show Alice's name, phone, and email decrypted and rendered in a neat profile card.
  7. Show checking a checkbox on a task: explain that clicking UI boxes transmits a command `complete task <id>` directly to the agent.
* **Audio/Voiceover**:
  > "Let's see Guardian in action. The dashboard is styled with premium glassmorphic grids. Right now, the vault is locked. Let's enter our passphrase. Once unlocked, the dashboard updates and displays our database statistics.
  > 
  > Let's add a contact with phone and email. Watch the **Security Guard** monitor on the right. The Sanitizer Agent instantly redacts the phone and email. 
  > 
  > In the chat console, we see the Coordinator Agent stream its chain-of-thought in real-time, executing the SQLite tools.
  > 
  > When we select the Contacts tab, we can see Alice's details are decrypted locally and displayed. If we inspect the raw SQLite file, all columns contain unreadable base64 cipher text."

---

## 🎬 Act 4: Custom MCP Server & Code Tour (3:15 - 4:15)

* **Visual**: Open code editor showing `mcp/secure_db_mcp.py` and run a quick command line query.
* **Audio/Voiceover**:
  > "Guardian is also equipped with a custom **Model Context Protocol** server. Implemented in Python, it communicates via stdin/stdout and exposes tools like `query_secure_vault` and `add_vault_note`. This means you can plug Guardian directly into developers' workspace tools like Claude Desktop or Cursor, enabling them to query your encrypted notes securely.
  > 
  > Let's look at the codebase. It's clean, lightweight, and written in Python. Here is the `security.py` file wrapping AES-GCM, and here is `sanitizer.py` managing regex redactions."

---

## 🎬 Act 5: Deployment & Wrap-Up (4:15 - 5:00)

* **Visual**: Show `Dockerfile` and the deployment instruction in `README.md`. Show the app running on a Render public URL.
* **Audio/Voiceover**:
  > "Deployability was a core goal. We mounted our static dashboard directly inside FastAPI, packaging the entire project into a single container. You can host Guardian locally using a single `docker-compose` command, or deploy it for free to platforms like Render in just a few clicks.
  > 
  > That is Guardian: a local-first, privacy-minded concierge agent system that keeps your data secure, unshared, and encrypted. Check out the GitHub repository for full code and setup instructions. Thanks for watching!"

---
*End of Video Script*
