// Guardian Frontend Application Controller

class GuardianApp {
    constructor() {
        this.passphrase = "guardian-default-passphrase";
        this.socket = null;
        this.activeTab = "notes";
        this.vaultData = { notes: [], tasks: [], contacts: [] };
        
        // Cache DOM Elements
        this.vaultStatus = document.getElementById("vaultStatus");
        this.passphraseInput = document.getElementById("passphraseInput");
        this.unlockBtn = document.getElementById("unlockBtn");
        this.userInput = document.getElementById("userInput");
        this.sendBtn = document.getElementById("sendBtn");
        this.chatForm = document.getElementById("chatForm");
        this.chatMessages = document.getElementById("chatMessages");
        this.dbSize = document.getElementById("dbSize");
        this.securityLogs = document.getElementById("securityLogs");
        this.clearLogsBtn = document.getElementById("clearLogsBtn");
        this.tabContent = document.getElementById("tabContent");
        
        // Stats Counters
        this.statNotesCount = document.querySelector("#statNotes .stat-count");
        this.statTasksCount = document.querySelector("#statTasks .stat-count");
        this.statContactsCount = document.querySelector("#statContacts .stat-count");
        
        // Bind Events
        this.unlockBtn.addEventListener("click", () => this.handleUnlock());
        this.chatForm.addEventListener("submit", (e) => this.handleChatSubmit(e));
        this.clearLogsBtn.addEventListener("click", () => this.clearSecurityLogs());
        
        // Tab setup
        document.querySelectorAll(".tab-btn").forEach(btn => {
            btn.addEventListener("click", (e) => this.switchTab(e.currentTarget));
        });
        
        // Initialize state
        this.updateUIState(false);
    }

    // Resolve API Endpoint base url dynamically for local vs cloud deployment
    getApiUrl() {
        const hostname = window.location.hostname;
        if (hostname === "localhost" || hostname === "127.0.0.1") {
            return "http://127.0.0.1:8000";
        }
        return window.location.origin; // Same host in cloud deployments
    }

    getWsUrl() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const hostname = window.location.hostname;
        if (hostname === "localhost" || hostname === "127.0.0.1") {
            return `${protocol}//127.0.0.1:8000/ws/chat`;
        }
        return `${protocol}//${window.location.host}/ws/chat`;
    }

    updateUIState(unlocked) {
        if (unlocked) {
            this.vaultStatus.classList.remove("locked");
            this.vaultStatus.classList.add("unlocked");
            this.vaultStatus.querySelector(".status-text").textContent = "Vault Unlocked";
            
            this.userInput.removeAttribute("disabled");
            this.sendBtn.removeAttribute("disabled");
            this.userInput.focus();
        } else {
            this.vaultStatus.classList.remove("unlocked");
            this.vaultStatus.classList.add("locked");
            this.vaultStatus.querySelector(".status-text").textContent = "Vault Locked";
            
            this.userInput.setAttribute("disabled", "true");
            this.sendBtn.setAttribute("disabled", "true");
            
            this.tabContent.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="lock"></i>
                    <p>Enter passphrase and click Unlock to open vault</p>
                </div>
            `;
            lucide.createIcons();
        }
    }

    async handleUnlock() {
        const enteredPassphrase = this.passphraseInput.value.trim();
        if (!enteredPassphrase) {
            alert("Please enter a valid passphrase to unlock the secure database.");
            return;
        }
        
        this.passphrase = enteredPassphrase;
        
        // Establish WebSocket Connection
        this.connectWebSocket();
    }

    connectWebSocket() {
        if (this.socket) {
            this.socket.close();
        }
        
        const wsUrl = this.getWsUrl();
        this.addSecurityLog("System", "Initiating secure WebSocket protocol...", "system-log");
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                // Send passphrase authentication payload
                this.socket.send(JSON.stringify({ passphrase: this.passphrase }));
            };
            
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleSocketMessage(data);
            };
            
            this.socket.onerror = (err) => {
                this.addSecurityLog("Error", "WebSocket connection failure.", "redaction-alert");
                console.error("WS error: ", err);
            };
            
            this.socket.onclose = () => {
                this.updateUIState(false);
                this.addSecurityLog("System", "Secure session closed. Vault locked.", "system-log");
            };
            
        } catch (e) {
            this.addSecurityLog("Error", `Socket open error: ${e.message}`, "redaction-alert");
        }
    }

    handleSocketMessage(data) {
        switch (data.type) {
            case "system":
                this.addSecurityLog("System", data.message, "system-log");
                this.updateUIState(true);
                this.fetchVaultData();
                break;
                
            case "status":
                this.updateActiveLoading(data.message);
                break;
                
            case "security_alert":
                this.addSecurityLog("Sanitizer", data.message, "redaction-alert");
                break;
                
            case "thought":
                this.appendThought(data.message);
                break;
                
            case "action":
                this.addSecurityLog("Coordinator", `Action: ${data.message}`, "action-log");
                this.appendActionBadge(data.message);
                break;
                
            case "response":
                this.renderFinalResponse(data.message);
                break;
                
            case "db_update":
                this.fetchVaultData();
                break;
                
            case "error":
                this.addSecurityLog("Exception", data.message, "redaction-alert");
                this.removeLoadingElement();
                break;
        }
    }

    // HTTP fetch stats & data
    async fetchVaultData() {
        const apiUrl = this.getApiUrl();
        try {
            // Fetch stats
            const statsRes = await fetch(`${apiUrl}/api/vault/stats?passphrase=${encodeURIComponent(this.passphrase)}`);
            if (statsRes.ok) {
                const stats = await statsRes.json();
                this.statNotesCount.textContent = stats.notes_count;
                this.statTasksCount.textContent = stats.pending_tasks_count;
                this.statContactsCount.textContent = stats.contacts_count;
                this.dbSize.textContent = `Size: ${(stats.db_size_bytes / 1024).toFixed(1)} KB`;
            }
            
            // Fetch decrypted data for lists
            const dataRes = await fetch(`${apiUrl}/api/vault/data?passphrase=${encodeURIComponent(this.passphrase)}`);
            if (dataRes.ok) {
                this.vaultData = await dataRes.json();
                this.renderTabContent();
            }
        } catch (e) {
            console.error("Failed to fetch vault statistics:", e);
        }
    }

    // Tabs Switching
    switchTab(targetElement) {
        document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
        targetElement.classList.add("active");
        
        this.activeTab = targetElement.getAttribute("data-tab");
        this.renderTabContent();
    }

    renderTabContent() {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        let html = "";
        
        if (this.activeTab === "notes") {
            const notes = this.vaultData.notes || [];
            if (notes.length === 0) {
                html = `<div class="empty-state"><i data-lucide="file-text"></i><p>No notes in the vault. Try asking the agent to add one.</p></div>`;
            } else {
                notes.forEach(note => {
                    html += `
                        <div class="note-item">
                            <h4>${this.escapeHtml(note.title)}</h4>
                            <p>${this.escapeHtml(note.content).replace(/\n/g, '<br>')}</p>
                            <button class="delete-vault-item" onclick="app.triggerDelete('note', ${note.id})"><i data-lucide="trash-2"></i></button>
                        </div>
                    `;
                });
            }
        } else if (this.activeTab === "tasks") {
            const tasks = this.vaultData.tasks || [];
            if (tasks.length === 0) {
                html = `<div class="empty-state"><i data-lucide="check-square"></i><p>No tasks found. Ask Guardian to add a task.</p></div>`;
            } else {
                tasks.forEach(task => {
                    const isCompleted = task.status === "completed";
                    html += `
                        <div class="task-item ${isCompleted ? 'completed' : ''}">
                            <div class="task-checkbox-container">
                                <input type="checkbox" class="task-checkbox" ${isCompleted ? 'checked' : ''} onchange="app.triggerComplete(${task.id}, this.checked)">
                                <span class="task-title">${this.escapeHtml(task.title)}</span>
                            </div>
                            <div class="task-meta">
                                ${task.due_date ? `<span class="task-due"><i data-lucide="calendar"></i> ${this.escapeHtml(task.due_date)}</span>` : ''}
                                <button class="delete-vault-item" style="position:static;" onclick="app.triggerDelete('task', ${task.id})"><i data-lucide="trash-2"></i></button>
                            </div>
                        </div>
                    `;
                });
            }
        } else if (this.activeTab === "contacts") {
            const contacts = this.vaultData.contacts || [];
            if (contacts.length === 0) {
                html = `<div class="empty-state"><i data-lucide="users"></i><p>Address book is empty. Add contacts via the agent console.</p></div>`;
            } else {
                contacts.forEach(contact => {
                    html += `
                        <div class="contact-item">
                            <div class="contact-name">${this.escapeHtml(contact.name)}</div>
                            <div class="contact-details">
                                ${contact.phone ? `<span><i data-lucide="phone"></i> ${this.escapeHtml(contact.phone)}</span>` : ''}
                                ${contact.email ? `<span><i data-lucide="mail"></i> ${this.escapeHtml(contact.email)}</span>` : ''}
                                ${contact.notes ? `<span><i data-lucide="info"></i> ${this.escapeHtml(contact.notes)}</span>` : ''}
                            </div>
                            <button class="delete-vault-item" onclick="app.triggerDelete('contact', ${contact.id})"><i data-lucide="trash-2"></i></button>
                        </div>
                    `;
                });
            }
        }
        
        this.tabContent.innerHTML = html;
        lucide.createIcons();
    }

    // Trigger actions from UI buttons (Task Checkbox and Delete icons)
    triggerDelete(type, id) {
        if (confirm(`Are you sure you want to delete this ${type} record?`)) {
            const command = `delete ${type} ${id}`;
            this.sendPrompt(command);
        }
    }

    triggerComplete(id, checked) {
        if (checked) {
            this.sendPrompt(`complete task ${id}`);
        }
    }

    // Send chat form submit
    handleChatSubmit(e) {
        e.preventDefault();
        const text = this.userInput.value.trim();
        if (!text) return;
        
        this.userInput.value = "";
        this.sendPrompt(text);
    }

    sendPrompt(text) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            alert("Secure session is not active. Unlock the vault first.");
            return;
        }

        // Render user message in chat
        this.appendUserMessage(text);
        
        // Show agent pending block
        this.createAgentLoadingBlock();

        // Send to socket
        this.socket.send(JSON.stringify({ prompt: text }));
    }

    // Chat rendering utilities
    appendUserMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message user-msg";
        msgDiv.innerHTML = `
            <div class="msg-icon"><i data-lucide="user"></i></div>
            <div class="msg-content">${this.escapeHtml(text)}</div>
        `;
        this.chatMessages.appendChild(msgDiv);
        this.scrollChat();
        lucide.createIcons();
    }

    createAgentLoadingBlock() {
        this.removeLoadingElement();
        
        const loaderDiv = document.createElement("div");
        loaderDiv.className = "message agent-msg";
        loaderDiv.id = "activeAgentMsg";
        loaderDiv.innerHTML = `
            <div class="msg-icon"><i data-lucide="bot"></i></div>
            <div class="msg-content">
                <div class="agent-status" id="activeAgentStatus">Initiating sanitization...</div>
                <div class="agent-thoughts" id="activeAgentThoughts" style="display:none;">
                    <div class="thought-header"><i data-lucide="brain-circuit"></i> Chain of Thought</div>
                    <div class="thoughts-list"></div>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(loaderDiv);
        this.scrollChat();
        lucide.createIcons();
    }

    updateActiveLoading(statusText) {
        const statusEl = document.getElementById("activeAgentStatus");
        if (statusEl) {
            statusEl.textContent = statusText;
        }
    }

    appendThought(thoughtText) {
        const thoughtsEl = document.getElementById("activeAgentThoughts");
        if (thoughtsEl) {
            thoughtsEl.style.display = "block";
            const listEl = thoughtsEl.querySelector(".thoughts-list");
            const stepDiv = document.createElement("div");
            stepDiv.className = "thought-step";
            stepDiv.innerHTML = `• ${this.escapeHtml(thoughtText)}`;
            listEl.appendChild(stepDiv);
            this.scrollChat();
        }
    }

    appendActionBadge(actionText) {
        const contentEl = document.querySelector("#activeAgentMsg .msg-content");
        if (contentEl) {
            const badge = document.createElement("div");
            badge.className = "agent-action";
            badge.innerHTML = `<i data-lucide="server"></i> ${this.escapeHtml(actionText)}`;
            contentEl.appendChild(badge);
            this.scrollChat();
            lucide.createIcons();
        }
    }

    renderFinalResponse(responseText) {
        const statusEl = document.getElementById("activeAgentStatus");
        if (statusEl) {
            statusEl.outerHTML = `<div style="white-space: pre-line;">${this.parseMarkdown(responseText)}</div>`;
        }
        
        // Clean ID so new requests create a fresh block
        const activeMsg = document.getElementById("activeAgentMsg");
        if (activeMsg) {
            activeMsg.removeAttribute("id");
        }
        
        this.scrollChat();
        lucide.createIcons();
    }

    removeLoadingElement() {
        const active = document.getElementById("activeAgentMsg");
        if (active) {
            active.remove();
        }
    }

    scrollChat() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    // Security guard logs utilities
    addSecurityLog(sender, message, logClass = "") {
        const timeStr = new Date().toLocaleTimeString();
        const entry = document.createElement("div");
        entry.className = `log-entry ${logClass}`;
        entry.innerHTML = `
            <span class="log-time">[${timeStr}] ${sender}</span>
            <p>${this.escapeHtml(message)}</p>
        `;
        this.securityLogs.appendChild(entry);
        this.securityLogs.scrollTop = this.securityLogs.scrollHeight;
    }

    async clearSecurityLogs() {
        const apiUrl = this.getApiUrl();
        try {
            await fetch(`${apiUrl}/api/security/logs/clear`, { method: "POST" });
            this.securityLogs.innerHTML = "";
            this.addSecurityLog("System", "Security monitoring log cleared.", "system-log");
        } catch(e) {
            console.error("Failed to clear logs:", e);
        }
    }

    // Helpers
    escapeHtml(text) {
        if (!text) return "";
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    parseMarkdown(text) {
        // Very basic parser for bold styling used in responses
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
    }
}

// Instantiate App
window.addEventListener("DOMContentLoaded", () => {
    window.app = new GuardianApp();
});
