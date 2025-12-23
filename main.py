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
    <title>Multiquip AI Agent Chatbot</title>
    <link rel="icon" type="image/png" href="/static/multiquip_title.png">
    
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        /* --- GLOBAL LAYOUT --- */
        * { box-sizing: border-box; }
        
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            color: #000000;
            overflow: hidden; /* No double scrollbars */
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100vh;
            margin: 0;
        }

        /* --- HEADER --- */
        .header {
            padding: 2px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #fff;
            flex-shrink: 0;
        }
        
        /* HEADER LOGO IMAGE (100px Height) */
        .logo-img {
            height: 100px;
            width: auto;
            display: block;
        }

        /* CLEAR BUTTON */
        .clear-btn {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        .clear-btn:hover { background-color: #d63c3c; }

        /* --- CHAT AREA --- */
        .chat-history {
            flex: 1;
            padding: 20px 10%; /* 10% side padding for readability */
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            background-color: #fff;
        }

        /* MESSAGE BUBBLES */
        .message-row {
            display: flex;
            width: 100%;
            margin-bottom: 10px;
        }
        .message-row.user { justify-content: flex-end; }
        .message-row.bot { justify-content: flex-start; }

        .message-bubble {
            max-width: 65%;
            padding: 15px 25px;
            border-radius: 12px;
            font-size: 16px;
            line-height: 1.6;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .user .message-bubble {
            background-color: #f0f2f6; /* Light Grey for User */
            color: #1f1f1f;
            border-bottom-right-radius: 2px;
        }

        .bot .message-bubble {
            background-color: #ffffff; /* White for Bot */
            border: 1px solid #e0e0e0;
            color: #1f1f1f;
            border-bottom-left-radius: 2px;
        }

        /* TABLE FORMATTING (INSIDE BUBBLES) */
        .message-bubble table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.95em;
            background-color: #fff;
        }
        .message-bubble th {
            background-color: #f4f4f4;
            font-weight: bold;
            text-align: left;
            border: 1px solid #ccc;
            padding: 12px;
        }
        .message-bubble td {
            border: 1px solid #ccc;
            padding: 12px;
            text-align: left;
        }
        .message-bubble tr:nth-child(even) {
            background-color: #fcfcfc;
        }

        /* GENERAL TEXT FORMATTING */
        .message-bubble p { margin-top: 0; margin-bottom: 10px; }
        .message-bubble ul { margin: 5px 0 10px 20px; }
        .message-bubble strong { font-weight: 700; color: #000; }

        /* --- FOOTER / INPUT AREA --- */
        .input-area {
            padding: 10px;
            background-color: #ffffff;
            border-top: 1px solid #e0e0e0;
            flex-shrink: 0;
        }

        .input-box {
            display: flex;
            gap: 15px;
            width: 100%;
            max-width: 1000px; /* WIDTH CONTROL: Change this to 800px or 1200px */
            margin: 0 auto;    /* Centers the box */
        }
        
        input[type="text"] {
            flex: 1;
            padding: 10px 25px;
            border: 1px solid #ddd;
            border-radius: 8px;
            outline: none;
            font-size: 16px;
            background-color: #f9f9f9;
        }
        input[type="text"]:focus {
            border-color: #888;
            background-color: #fff;
            box-shadow: 0 0 0 2px rgba(0,0,0,0.05);
        }
        button.send-btn {
            padding: 0 40px;
            background-color: #1f1f1f;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
        }
        button.send-btn:hover { background-color: #000; }
        
        /* AVATARS */
        .avatar-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            margin: 0 15px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .user .avatar-icon { order: 2; background-color: #4b6ef7; color: white; margin-left: 15px; margin-right: 0;}
        .bot .avatar-icon { order: 1; background-color: #ff9f43; color: white; margin-right: 15px; margin-left: 0;}

    </style>
</head>
<body>

<div class="chat-container">
    <div class="header">
        <div style="display: flex; align-items: center;">
            <img src="/static/multiquip.png" alt="Multiquip" class="logo-img" onerror="this.style.display='none'; document.getElementById('fallback-title').style.display='block';">
            <span id="fallback-title" style="display: none; font-weight: bold; font-size: 24px;">Multiquip</span>
        </div>
        <button class="clear-btn" onclick="clearChat()">🗑️ Clear Conversation</button>
    </div>

    <div class="chat-history" id="chat-box">
        <div class="message-row bot">
            <div class="avatar-icon">🤖</div>
            <div class="message-bubble">
                <p>Hello! I am your Multiquip Assistant.</p>
            </div>
        </div>
    </div>

    <div class="input-area">
        <form class="input-box" onsubmit="sendMessage(event)">
            <input type="text" id="user-input" placeholder="Type your question here..." autocomplete="off">
            <button type="submit" class="send-btn" id="send-btn">Send</button>
        </form>
    </div>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const inputField = document.getElementById('user-input');

    // Display Message Function
    function appendMessage(role, text, isHtml = false) {
        const rowDiv = document.createElement('div');
        rowDiv.className = `message-row ${role}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar-icon';
        avatarDiv.innerText = role === 'user' ? '👤' : '🤖';

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

    // Send Message Logic
    async function sendMessage(e) {
        e.preventDefault();
        const message = inputField.value.trim();
        if (!message) return;

        appendMessage('user', message, false);
        inputField.value = '';
        inputField.disabled = true;

        // Add Loading Spinner
        const loadingId = 'loading-' + Date.now();
        const loadingRow = document.createElement('div');
        loadingRow.className = 'message-row bot';
        loadingRow.id = loadingId;
        loadingRow.innerHTML = `
            <div class="avatar-icon">🤖</div>
            <div class="message-bubble" style="color: #666;">Thinking...</div>
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
        appendMessage('bot', 'Conversation cleared.', false);
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
            # Handle various Boomi response shapes
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

# ==========================================
# IMAGE SERVING (This finds multiquip.png)
# ==========================================
# This allows the HTML to access 'multiquip.png' from the current folder
if os.path.exists("multiquip.png"):
    # We mount the current directory "." to the URL path "/static"
    app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)