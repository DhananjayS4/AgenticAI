⏱️ Act 1: Intro & The Privacy Problem (0:00 - 0:45)
Visuals:

Start with the Web UI dashboard open in your browser (http://localhost:8000), showing the lock screen: a premium dark interface with a glowing lock icon saying "Vault Locked".
Cursor hovering over the passphrase input field.
Spoken Script:

"AI agents are incredibly powerful, but to be truly useful, they need access to our most private information: server credentials, secret keys, daily tasks, and contact information.

Typically, when you use a cloud-based agent, this private data is sent directly to external LLM servers in plain text. If the database is breached, or the LLM provider's logs are exposed, your privacy is compromised.

Meet Guardian—a zero-trust, local-first personal assistant. Guardian encrypts your local database on-disk using AES-256-GCM, and dynamically redacts all sensitive PII from your prompts before they ever leave your machine. Let's unlock the vault and see it in action."

⏱️ Act 2: Live Dashboard & PII Redaction Demo (0:45 - 2:15)
Visuals:

Type guardian-default-passphrase into the password field and click Unlock Vault.
Action: The dashboard transitions to show stats cards updating with a glowing green pulse.
Type this exact command into the Concierge Console chat input:
text
add contact "Alice Smith" phone "555-123-4567" email "alice.smith@example.com" notes "Database password is rootpwd123"
Press Enter.
Action: Zoom in on the Security Guard panel (right column) to show the log messages scrolling:
Security Alert: Redacted phone '555...567' to [REDACTED_PHONE_1]
Security Alert: Redacted email 'ali...com' to [REDACTED_EMAIL_1]
Security Alert: Redacted credential in expression: 'password = ...'
Point to the Concierge Console thought log stream showing:
Analyzing sanitized input...
Intent identified: ADD_CONTACT...
AES-256-GCM encryption complete.
Click on the Contacts tab (middle panel) to show Alice Smith's profile card, displaying her decrypted phone, email, and password notes.
Spoken Script:

"I'll enter my security passphrase to unlock the vault. As soon as the vault is unlocked, our local FastAPI database engine establishes an in-memory decryption key derived using PBKDF2.

Now, watch this. I'll add a new contact containing sensitive details: a phone number, email, and a password secret. Before this prompt is processed, Guardian's local PII Sanitizer Agent intercepts it.

Look at the Security Guard log on the right. The agent instantly redacted the phone, email, and password, replacing them with secure tokens. The Coordinator Agent processed the sanitized prompt, mapped the database intent, and wrote the details to SQLite.

If I select the Contacts tab, we see Alice's details are decrypted in memory and shown here. But on disk, the database stores only raw AES ciphertext."

⏱️ Act 3: Database Decryption & Code Tour (2:15 - 3:30)
Visuals:

Switch to your code editor showing the database file vault.db or open backend/security.py.
Scroll to showing SecurityManager with AESGCM and PBKDF2HMAC configuration.
Switch to backend/agents/sanitizer.py to highlight the regular expression patterns.
Spoken Script:

*"Let's take a look under the hood. All data at rest is secured inside an SQLite database using AES-256-GCM.

Here in security.py, we use the cryptography library to derive a 256-bit key from the user's passphrase. Each string is encrypted using a unique 12-byte initialization vector, meaning no two entries of the same data yield the same ciphertext.

Over in sanitizer.py, we define regex rules for emails, phones, SSNs, credit cards, and API secrets. The Sanitizer strips these elements from the user prompt and stores the mapping in local volatile memory. The Coordinator restores the original values only at the moment of database write or local search, keeping them out of external LLM server calls."*

⏱️ Act 4: Custom MCP Server Demo (3:30 - 4:15)
Visuals:

Switch your editor to mcp/secure_db_mcp.py.
Highlight the tools array showing query_secure_vault and add_vault_note.
Spoken Script:

*"Guardian also features a custom Model Context Protocol (MCP) server.

In mcp/secure_db_mcp.py, we expose tools like query_secure_vault and add_vault_note over standard JSON-RPC. This allows other developer tools like Claude Desktop or Cursor to securely query or add notes directly in your encrypted local data vault. The external agents call these standard tools locally, maintaining zero-trust architecture."*

⏱️ Act 5: Cloud Deployment & Wrap-Up (4:15 - 5:00)
Visuals:

Show your render.yaml file in the code editor.
Open the browser and show the project's GitHub page with README.md and the glowing banner.
Spoken Script:

*"Finally, deployment is straightforward. We've packaged the frontend dashboard and backend API inside a unified service.

By using the provided render.yaml blueprint, you can deploy your secure fleet to Render with a single click, entering your Gemini API key securely in the cloud environment.

That is Guardian: keeping your concierge assistant smart, and your personal data secure. Thank you for watching!"*
