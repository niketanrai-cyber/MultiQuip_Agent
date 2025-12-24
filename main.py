from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import uvicorn
import os

app = FastAPI()

# ==========================================
# BOOMI CONFIGURATION
# ==========================================
BOOMI_URL = "https://c02-usa-west.integrate-test.boomi.com/ws/simple/createGetAIData"
BOOMI_USERNAME = "Chatbot-POC@multiquipinc-U9F4Z5.0FN17D"
BOOMI_PASSWORD = "f9c03846-70a1-4d53-bc80-bab2cfdfe35d"

# ==========================================
# HTML & CSS UI
# ==========================================
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multiquip Chatbot</title>
    
    <link rel="icon" type="image/png" href="/static/multiquip_title.png">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        /* --- THEME VARIABLES --- */
        :root {
            /* Light Mode */
            --bg-color: #ffffff;
            --aurora-end: #e0f2fe; /* Soft Light Blue for bottom fade */
            
            --text-color: #000000;
            --header-bg: #ffffff;
            --border-color: #e0e0e0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            
            --user-bubble-bg: #f0f2f6;
            --user-text-color: #000000;
            
            --bot-bubble-bg: #ffffff;
            --bot-text-color: #0056b3; 
            
            --input-area-bg: #ffffff;
            --input-box-bg: #f9f9f9;
            --input-border: #ddd;
            
            /* Icon Container Colors */
            --icon-bg-user: transparent;
            --icon-bg-bot: transparent;
            
            /* --- VECTOR COLORS --- */
            
            /* Robot */
            --bot-outline: #103f54;
            --bot-face: #e0f7fa;
            --bot-body: #cfd8dc;
            --bot-cheek: #f48fb1;

            /* User */
            --user-outline: #37474f;
            --user-skin: #ffe0b2;
            --user-hair: #5d4037;
            --user-shirt: #90caf9;
        }

        body.dark-mode {
            /* Dark Mode */
            --bg-color: #121212;
            --aurora-end: #1e293b; 
            
            --text-color: #ffffff;
            --header-bg: #1e1e1e;
            --border-color: #333333;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.5);
            
            --user-bubble-bg: #2c2c2c;
            --user-text-color: #ffffff;
            
            --bot-bubble-bg: #1e1e1e;
            --bot-text-color: #66b2ff; 
            
            --input-area-bg: #1e1e1e;
            --input-box-bg: #2c2c2c;
            --input-border: #444;

            /* Vector Colors (Dark Mode) */
            --bot-outline: #81d4fa;
            --bot-face: #263238;
            --bot-body: #37474f;
            --bot-cheek: #ec407a;

            /* User (Dark Mode) */
            --user-outline: #eceff1;
            --user-skin: #5d4037;
            --user-hair: #d7ccc8;
            --user-shirt: #1565c0;
        }

        /* --- GLOBAL --- */
        * { box-sizing: border-box; }
        body, html {
            margin: 0; padding: 0; width: 100%; height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            
            /* BACKGROUND: Soft Aurora Gradient */
            background: linear-gradient(180deg, var(--bg-color) 60%, var(--aurora-end) 100%);
            background-attachment: fixed;
            
            color: var(--text-color);
            overflow: hidden;
            transition: background 0.3s, color 0.3s;
        }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 4px; }
        body.dark-mode ::-webkit-scrollbar-thumb { background-color: #444; }

        .chat-container {
            display: flex; flex-direction: column; width: 100%; height: 100vh;
        }

        /* --- HEADER --- */
        .header {
            padding: 10px 30px;
            border-bottom: 1px solid var(--border-color);
            display: flex; justify-content: space-between; align-items: center;
            background-color: var(--header-bg);
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
            z-index: 10;
        }
        
        .logo-img { height: 100px; width: auto; display: block; }
        .header-controls { display: flex; gap: 10px; }

        .btn {
            border: none; padding: 8px 15px; border-radius: 6px;
            cursor: pointer; font-size: 14px; font-weight: 600;
        }
        .clear-btn { background-color: #ff4b4b; color: white; }
        .clear-btn:hover { background-color: #d63c3c; }
        .theme-btn { 
            background-color: transparent; 
            border: 1px solid var(--border-color);
            color: var(--text-color);
            font-size: 18px; padding: 8px 12px; 
        }

        /* --- CHAT HISTORY --- */
        .chat-history {
            flex: 1; padding: 20px 10%; overflow-y: auto;
            display: flex; flex-direction: column; gap: 20px;
            background-color: transparent; 
        }

        .message-row { display: flex; width: 100%; margin-bottom: 10px; }
        .message-row.user { justify-content: flex-end; }
        .message-row.bot { justify-content: flex-start; }

        .message-bubble {
            max-width: 65%; padding: 15px 25px; border-radius: 12px;
            font-size: 16px; line-height: 1.6; position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            
            /* Ensure text wraps to prevent bubble expansion */
            overflow-wrap: break-word; 
            word-wrap: break-word; 
        }

        /* Colors */
        .user .message-bubble {
            background-color: var(--user-bubble-bg);
            color: var(--user-text-color);
            border-bottom-right-radius: 2px;
        }
        .bot .message-bubble {
            background-color: var(--bot-bubble-bg);
            border: 1px solid var(--border-color);
            color: var(--bot-text-color);
            border-bottom-left-radius: 2px;
        }
        .bot .message-bubble * { color: var(--bot-text-color); }

        /* --- MODERN AVATAR CONTAINER --- */
        .avatar-icon {
            width: 65px; height: 65px; 
            display: flex; align-items: center; justify-content: center;
            border-radius: 12px;
            margin: 0 15px; flex-shrink: 0;
            transition: all 0.3s ease;
            background: transparent; 
        }
        
        .user .avatar-icon { order: 2; margin-left: 15px; margin-right: 0; }
        .bot .avatar-icon { order: 1; margin-right: 15px; margin-left: 0; }

        /* --- VECTOR SVG STYLING --- */
        .char-svg { width: 100%; height: 100%; overflow: visible; }

        /* Robot CSS Variables */
        .bot-stroke { stroke: var(--bot-outline); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
        .bot-fill-face { fill: var(--bot-face); }
        .bot-fill-body { fill: var(--bot-body); }
        .bot-eye { fill: var(--bot-outline); stroke: none; }
        .bot-cheek { fill: var(--bot-cheek); opacity: 0.6; stroke: none; }

        /* User CSS Variables */
        .user-stroke { stroke: var(--user-outline); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
        .user-fill-skin { fill: var(--user-skin); }
        .user-fill-hair { fill: var(--user-hair); }
        .user-fill-shirt { fill: var(--user-shirt); }
        .user-eye { fill: var(--user-outline); stroke: none; }


        /* --- ANIMATIONS --- */
        @keyframes botFloat { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0px); } }
        .anim-bot-idle { animation: botFloat 3s ease-in-out infinite; }

        @keyframes userBreathe { 0% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-3px) scale(1.02); } 100% { transform: translateY(0px) scale(1); } }
        .anim-user-idle { animation: userBreathe 4.5s ease-in-out infinite; }

        @keyframes heartbeat { 0% { transform: scale(1); } 15% { transform: scale(1.1); } 30% { transform: scale(1); } 45% { transform: scale(1.1); } 60% { transform: scale(1); } 100% { transform: scale(1); } }
        @keyframes blink { 0%, 90%, 100% { transform: scaleY(1); } 95% { transform: scaleY(0.1); } }
        
        .anim-bot-thinking { animation: heartbeat 1.5s infinite ease-in-out; }
        .anim-bot-thinking .bot-eye { transform-origin: center; animation: blink 2s infinite; }


        /* --- TABLE FIX (Keeps content inside bubble) --- */
        .message-bubble table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0; 
            font-size: 0.9em; 
            
            /* Strict Layout Control */
            table-layout: fixed; /* Forces table to fit in 100% width */
            word-wrap: break-word; /* Breaks long words if needed */
        }

        .message-bubble th { 
            background-color: rgba(0,0,0,0.05); 
            font-weight: bold; 
            text-align: left; 
            border: 1px solid var(--border-color); 
            padding: 8px; 
            overflow: hidden; 
        }

        .message-bubble td { 
            border: 1px solid var(--border-color); 
            padding: 8px; 
            text-align: left; 
            
            /* Wrap Text */
            word-break: break-word; 
            overflow-wrap: break-word;
        }


        /* Typing Indicator */
        .typing-indicator span {
            display: inline-block; width: 6px; height: 6px;
            background-color: var(--bot-text-color); border-radius: 50%;
            margin-right: 4px; opacity: 0.6;
            animation: typing 1.4s infinite ease-in-out both;
        }
        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }

        /* --- FOOTER --- */
        .input-area {
            padding: 15px;
            background-color: var(--input-area-bg);
            border-top: 1px solid var(--border-color);
            flex-shrink: 0;
            box-shadow: 0 -1px 3px rgba(0,0,0,0.05);
        }
        .input-box {
            display: flex; gap: 15px; width: 100%; max-width: 700px;
            margin: 0 auto; align-items: center; 
        }
        input[type="text"] {
            flex: 1; padding: 12px 20px;
            border: 1px solid var(--input-border);
            border-radius: 8px; outline: none; font-size: 16px;
            background-color: var(--input-box-bg);
            color: var(--text-color);
            height: 48px; 
        }
        input[type="text"]:focus {
            border-color: #888;
            box-shadow: 0 0 0 2px rgba(0,0,0,0.05);
        }

        button.send-btn {
            background-color: #1f1f1f; border: none; border-radius: 10px;
            width: 48px; height: 48px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            padding: 0; flex-shrink: 0; transition: all 0.2s ease;
        }
        button.send-btn:hover { background-color: #000; transform: scale(1.05); }
        body.dark-mode button.send-btn { background-color: #ffffff; }
        body.dark-mode button.send-btn:hover { background-color: #e0e0e0; }
        
        button.send-btn svg { width: 22px; height: 22px; fill: white; margin-left: 2px; margin-top: 2px; }
        body.dark-mode button.send-btn svg { fill: #000000; }

    </style>
</head>
<body>

<div class="chat-container">
    <div class="header">
        <div style="display: flex; align-items: center;">
            <img src="/static/multiquip.png" alt="Multiquip" class="logo-img" onerror="this.style.display='none'; document.getElementById('fallback-title').style.display='block';">
            <span id="fallback-title" style="display: none; font-weight: bold; font-size: 24px;">Multiquip</span>
        </div>
        
        <div class="header-controls">
            <button class="btn theme-btn" onclick="toggleTheme()" title="Toggle Dark Mode">
                <span id="theme-icon">🌙</span>
            </button>
            <button class="btn clear-btn" onclick="clearChat()">🗑️ Clear</button>
        </div>
    </div>

    <div class="chat-history" id="chat-box">
        </div>

    <div class="input-area">
        <form class="input-box" onsubmit="sendMessage(event)">
            <input type="text" id="user-input" placeholder="Type your question here..." autocomplete="off">
            <button type="submit" class="send-btn" id="send-btn">
                <svg viewBox="0 0 24 24">
                   <path d="M22,2L2,10L9,13.5L16.5,7.5L10.5,15L14,22L22,2Z" />
                </svg>
            </button>
        </form>
    </div>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const inputField = document.getElementById('user-input');
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');

    // ===========================================
    // VECTOR ASSETS (SVGs)
    // ===========================================

    // 1. ROBOT DEFINITION
    const ROBOT_DRAWING = `
        <svg viewBox="0 0 100 100" class="char-svg">
            <line x1="50" y1="20" x2="50" y2="10" class="bot-stroke" />
            <circle cx="50" cy="8" r="4" class="bot-stroke bot-fill-body" />
            <path d="M25,50 Q20,50 20,40 Q20,30 25,30" class="bot-stroke bot-fill-body" />
            <path d="M75,50 Q80,50 80,40 Q80,30 75,30" class="bot-stroke bot-fill-body" />
            <path d="M30,80 Q50,95 70,80 L70,70 L30,70 Z" class="bot-stroke bot-fill-body" />
            <rect x="25" y="25" width="50" height="45" rx="18" class="bot-stroke bot-fill-face" />
            <circle cx="40" cy="45" r="4" class="bot-eye" />
            <circle cx="60" cy="45" r="4" class="bot-eye" />
            <path d="M42,55 Q50,62 58,55" class="bot-stroke" style="stroke-width: 2;" />
            <circle cx="34" cy="50" r="3" class="bot-cheek" />
            <circle cx="66" cy="50" r="3" class="bot-cheek" />
        </svg>
    `;

    // 2. ROBOT THINKING
    const ROBOT_THINKING_DRAWING = `
        <svg viewBox="0 0 100 100" class="char-svg">
            <line x1="85" y1="20" x2="90" y2="15" class="bot-stroke" style="stroke: #ff9800;" />
            <line x1="88" y1="28" x2="94" y2="28" class="bot-stroke" style="stroke: #ff9800;" />
            <line x1="50" y1="20" x2="50" y2="10" class="bot-stroke" />
            <circle cx="50" cy="8" r="4" class="bot-stroke bot-fill-body" />
            <path d="M25,50 Q20,50 20,40 Q20,30 25,30" class="bot-stroke bot-fill-body" />
            <path d="M75,50 Q80,50 80,40 Q80,30 75,30" class="bot-stroke bot-fill-body" />
            <path d="M30,80 Q50,95 70,80 L70,70 L30,70 Z" class="bot-stroke bot-fill-body" />
            <rect x="25" y="25" width="50" height="45" rx="18" class="bot-stroke bot-fill-face" />
            <circle cx="40" cy="43" r="4" class="bot-eye" />
            <circle cx="60" cy="43" r="4" class="bot-eye" />
            <path d="M45,55 Q50,55 55,55" class="bot-stroke" style="stroke-width: 2;" />
        </svg>
    `;

    // 3. USER DEFINITION
    const USER_DRAWING = `
        <svg viewBox="0 0 100 100" class="char-svg">
            <path d="M20,85 Q50,95 80,85 L80,75 Q80,65 65,65 L35,65 Q20,65 20,75 Z" class="user-stroke user-fill-shirt" />
            <circle cx="50" cy="45" r="22" class="user-stroke user-fill-skin" />
            <path d="M28,40 Q25,20 50,15 Q75,20 72,40 Q75,30 50,25 Q30,30 28,40" class="user-stroke user-fill-hair" />
            <circle cx="43" cy="48" r="3" class="user-eye" />
            <circle cx="57" cy="48" r="3" class="user-eye" />
            <path d="M45,58 Q50,62 55,58" class="user-stroke" style="stroke-width: 2;" />
        </svg>
    `;

    // Combine them with animation classes
    const BOT_IDLE_HTML = `<div class="anim-bot-idle">${ROBOT_DRAWING}</div>`;
    const BOT_THINKING_HTML = `<div class="anim-bot-thinking">${ROBOT_THINKING_DRAWING}</div>`;
    const USER_HTML = `<div class="anim-user-idle">${USER_DRAWING}</div>`;


    // --- THEME LOGIC ---
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        themeIcon.innerText = '☀️';
    }

    function toggleTheme() {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            themeIcon.innerText = '☀️';
        } else {
            localStorage.setItem('theme', 'light');
            themeIcon.innerText = '🌙';
        }
    }

    // --- CHAT LOGIC ---

    // Initialize first message
    window.onload = function() {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'message-row bot';
        rowDiv.innerHTML = `
            <div class="avatar-icon">${BOT_IDLE_HTML}</div>
            <div class="message-bubble"><p>Hello! I am your Multiquip Assistant.</p></div>
        `;
        chatBox.appendChild(rowDiv);
    }

    function appendMessage(role, text, isHtml = false) {
        const rowDiv = document.createElement('div');
        rowDiv.className = `message-row ${role}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar-icon';
        
        avatarDiv.innerHTML = role === 'user' ? USER_HTML : BOT_IDLE_HTML;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        if (isHtml) {
            bubbleDiv.innerHTML = marked.parse(text); 
        } else {
            bubbleDiv.innerText = text;
        }
        
        rowDiv.appendChild(avatarDiv);
        rowDiv.appendChild(bubbleDiv);
        chatBox.appendChild(rowDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage(e) {
        e.preventDefault();
        const message = inputField.value.trim();
        if (!message) return;

        appendMessage('user', message, false);
        inputField.value = '';
        inputField.disabled = true;

        const loadingId = 'loading-' + Date.now();
        const loadingRow = document.createElement('div');
        loadingRow.className = 'message-row bot';
        loadingRow.id = loadingId;
        
        loadingRow.innerHTML = `
            <div class="avatar-icon">${BOT_THINKING_HTML}</div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatBox.appendChild(loadingRow);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            
            document.getElementById(loadingId).remove();
            appendMessage('bot', data.reply, true);
            
        } catch (error) {
            document.getElementById(loadingId).remove();
            appendMessage('bot', '⚠️ Error: Could not connect to the server.', false);
        } finally {
            inputField.disabled = false;
            inputField.focus();
        }
    }

    function clearChat() {
        chatBox.innerHTML = '';
        const rowDiv = document.createElement('div');
        rowDiv.className = 'message-row bot';
        rowDiv.innerHTML = `
            <div class="avatar-icon">${BOT_IDLE_HTML}</div>
            <div class="message-bubble"><p>Conversation cleared.</p></div>
        `;
        chatBox.appendChild(rowDiv);
    }
</script>

</body>
</html>
"""

# ==========================================
# SERVER LOGIC
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_endpoint(payload: dict):
    user_message = payload.get("message", "")
    try:
        response = requests.post(
            BOOMI_URL,
            headers={"Content-Type": "text/plain"},
            data=user_message,
            auth=(BOOMI_USERNAME, BOOMI_PASSWORD),
            timeout=120
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                content = data[0].get("content", "No content")
            elif isinstance(data, dict):
                content = data.get("content", "No content")
            else:
                content = "Empty response"
            return {"reply": content}
        else:
            return {"reply": f"**Error {response.status_code}:** Unable to fetch data."}
    except Exception as e:
        return {"reply": f"**System Error:** {str(e)}"}

if os.path.exists("multiquip.png"):
    app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)