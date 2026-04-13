let ws;
let typingTimeout;
let pingInterval;
let currentRoom = "";

let dmTypingTimeout;

let currentUsername = "";
let currentDMTarget = "";

let chatHistoryMembers = new Set();

function toggleHistory() {
    const dmPanel = document.getElementById("dm-panel");
    const historyPanel = document.getElementById("history-panel");
    if (dmPanel.style.display === "flex") {
        closeDM();
        historyPanel.classList.remove("collapsed");
    } else {
        historyPanel.classList.toggle("collapsed");
    }
}

function renderHistory() {
    const list = document.getElementById("history-list");
    list.innerHTML = "";
    chatHistoryMembers.forEach(user => {
        const div = document.createElement("div");
        div.className = "history-item";
        if (user === currentDMTarget) div.classList.add("active");
        div.innerText = user;
        div.onclick = () => openDM(user);
        list.appendChild(div);
    });
}

function getTimeString(dateStr = null) {
    const d = dateStr ? new Date(dateStr + "Z") : new Date(); // add Z if string is naive UTC
    return `[${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}]`;
}

function connect() {
    const username = document.getElementById("username").value;
    const room = document.getElementById("room").value || "#general";

    if (!username) {
        alert("Username is required");
        return;
    }

    currentUsername = username;
    currentRoom = room;

    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
        // Switch UI
        document.getElementById("login").style.display = "none";
        document.getElementById("app").style.display = "flex";
        
        document.getElementById("room-header-text").innerText = `${currentRoom} | 1 members online`;

        console.log(`=== Client View (${currentUsername}) ===`);
        console.log(`${currentRoom} | 1 members online`);
        console.log(`──────────────────────────────`);

        // Send initial connection event with username
        ws.send(JSON.stringify({ type: "init", username: username }));
        
        // Auto join
        ws.send(JSON.stringify({ type: "join", room: currentRoom }));

        // Start heartbeat
        pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ping" }));
            }
        }, 15000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const chat = document.getElementById("chat");

        if (data.type === "message") {
            const timeStr = getTimeString(data.timestamp);
            const isSystem = data.sender === "System";
            const senderSpan = isSystem ? `<span class="system">${data.sender}</span>` : `<span class="sender">${data.sender}</span>`;
            chat.innerHTML += `<div class="message"><span class="timestamp">${timeStr}</span> ${senderSpan}: ${data.text}</div>`;
            chat.scrollTop = chat.scrollHeight;
            
            if (!isSystem) {
                console.log(`${timeStr} ${data.sender}: ${data.text}`);
            }
            
            const ind = document.getElementById("typing-indicator");
            if (ind) ind.style.display = "none";
        } else if (data.type === "dm") {
            chatHistoryMembers.add(data.sender);
            renderHistory();
            
            const timeStr = getTimeString();
            const targetChat = document.getElementById("dm-chat");
            targetChat.innerHTML += `<div class="message"><span class="timestamp">${timeStr}</span> <span class="system">[DM from ${data.sender}]</span>: ${data.text}</div>`;
            targetChat.scrollTop = targetChat.scrollHeight;
            
            // Auto open dm panel if closed
            if (document.getElementById("dm-panel").style.display !== "flex") {
                openDM(data.sender);
            }
            
            const ind = document.getElementById("dm-typing-indicator");
            if (ind) ind.style.display = "none";
        } else if (data.type === "dm_typing") {
            const ind = document.getElementById("dm-typing-indicator");
            if (ind) {
                ind.style.display = "block";
                const timeStr = getTimeString();
                ind.innerHTML = `<span class="timestamp">${timeStr}</span>Typing...`;
                
                clearTimeout(dmTypingTimeout);
                dmTypingTimeout = setTimeout(() => {
                    ind.style.display = "none";
                }, 5000);
            }
        } else if (data.type === "typing") {
            if (data.sender === currentUsername) return; // Hide own typing indicator
            
            const ind = document.getElementById("typing-indicator");
            if (ind) {
                ind.style.display = "block";
                const timeStr = getTimeString();
                ind.innerHTML = `<span class="timestamp">${timeStr}</span> ${data.sender} is typing...`;
                
                console.log(`${timeStr} ${data.sender} is typing...`);
                
                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(() => {
                    ind.style.display = "none";
                }, 5000);
            }
        } else if (data.type === "presence") {
            const usersList = Object.entries(data.data)
                .map(([u, status]) => {
                    const youStr = (u === currentUsername) ? " (You)" : "";
                    const dot = status === "online" ? `<span class="online-dot"></span>` : `<span class="offline-dot"></span>`;
                    return `<div class="user-item" onclick="openDM('${u}')">${dot} ${u}${youStr}</div>`;
                })
                .join("");
            document.getElementById("presence").innerHTML = usersList;
        } else if (data.type === "room_info") {
            if (data.room === currentRoom) {
                document.getElementById("room-header-text").innerText = `${currentRoom} | ${data.count} members online`;
            }
        } else if (data.type === "warning") {
            chat.innerHTML += `<div class="message"><span class="timestamp">${getTimeString()}</span> <span style="color:orange;">[WARNING] ${data.text}</span></div>`;
        } else if (data.type === "error") {
            chat.innerHTML += `<div class="message"><span class="timestamp">${getTimeString()}</span> <span style="color:red;">[ERROR] ${data.text}</span></div>`;
        }
    };

    ws.onerror = (error) => {
        console.error("WebSocket error observed:", error);
    };

    ws.onclose = (event) => {
        clearInterval(pingInterval);
        document.getElementById("chat").innerHTML += `<div class="message"><span class="timestamp">${getTimeString()}</span> <span style="color:red;">Disconnected from server (Code: ${event.code})</span></div>`;
    };
}

function sendMsg() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const msgInput = document.getElementById("msg");
    const msg = msgInput.value;
    if (!msg.trim()) return;
    
    if (msg.startsWith("/dm ")) {
        const parts = msg.split(" ");
        if (parts.length > 2) {
            const to = parts[1];
            const text = parts.slice(2).join(" ");
            ws.send(JSON.stringify({ type: "dm", to: to, text: text }));
            const chat = document.getElementById("chat");
            chat.innerHTML += `<div class="message"><span class="timestamp">${getTimeString()}</span> <span class="system">[DM to ${to}]</span>: ${text}</div>`;
            chat.scrollTop = chat.scrollHeight;
        }
    } else {
        ws.send(JSON.stringify({
            type: "message",
            text: msg
        }));
    }
    msgInput.value = "";
}

function sendDMMsg() {
    if (!ws || ws.readyState !== WebSocket.OPEN || !currentDMTarget) return;

    const msgInput = document.getElementById("dm-msg");
    const msg = msgInput.value;
    if (!msg.trim()) return;
    
    chatHistoryMembers.add(currentDMTarget);
    renderHistory();
    
    ws.send(JSON.stringify({ type: "dm", to: currentDMTarget, text: msg }));
    
    const targetChat = document.getElementById("dm-chat");
    targetChat.innerHTML += `<div class="message"><span class="timestamp">${getTimeString()}</span> <span class="system">[DM to ${currentDMTarget}]</span>: ${msg}</div>`;
    targetChat.scrollTop = targetChat.scrollHeight;
    
    msgInput.value = "";
}

function openDM(targetUser) {
    if (targetUser === currentUsername) return; // Can't DM yourself
    currentDMTarget = targetUser;
    
    chatHistoryMembers.add(targetUser);
    renderHistory();
    
    document.getElementById("dm-target").innerText = targetUser;
    document.getElementById("dm-panel").style.display = "flex";
}

function closeDM() {
    document.getElementById("dm-panel").style.display = "none";
    currentDMTarget = "";
    renderHistory();
}

function sendTyping() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "typing" }));
    }
}

function sendDMTyping() {
    if (ws && ws.readyState === WebSocket.OPEN && currentDMTarget) {
        ws.send(JSON.stringify({ type: "dm_typing", to: currentDMTarget }));
    }
}