from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import uvicorn
import os
from collections import deque

app = FastAPI()

# ==========================================
# BOOMI CONFIGURATION
# ==========================================
BOOMI_URL = "https://c02-usa-west.integrate-test.boomi.com/ws/simple/createGetAIData"
BOOMI_USERNAME = "Chatbot-POC@multiquipinc-U9F4Z5.0FN17D"
BOOMI_PASSWORD = "f9c03846-70a1-4d53-bc80-bab2cfdfe35d"

# ==========================================
# MEMORY STORAGE
# ==========================================
# Stores the last 10 messages for every active user session.
session_storage = {} 

# ==========================================
# HTML & CSS UI (FULL VERSION)
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
            --aurora-end: #e0f2fe;
            
            --text-color: #333333;
            --heading-color: #103f54; 
            --header-bg: #ffffff;
            --border-color: #e0e0e0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            
            --user-bubble-bg: #f0f2f6;
            --user-text-color: #000000;
            
            --bot-bubble-bg: #ffffff;
            --bot-text-color: #0056b3; 
            
            --input-area-bg: rgba(255, 255, 255, 0.9);
            --input-box-bg: #f9f9f9;
            --input-border: #ddd;
            
            /* Vector Colors */
            --bot-outline: #103f54;
            --bot-face: #e0f7fa;
            --bot-body: #cfd8dc;
            --bot-cheek: #f48fb1;

            --user-outline: #37474f;
            --user-skin: #ffe0b2;
            --user-hair: #5d4037;
            --user-shirt: #90caf9;
        }

        body.dark-mode {
            /* Dark Mode */
            --bg-color: #121212;
            --aurora-end: #1e293b; 
            
            --text-color: #e0e0e0;
            --heading-color: #81d4fa;
            --header-bg: #1e1e1e;
            --border-color: #333333;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.5);
            
            --user-bubble-bg: #2c2c2c;
            --user-text-color: #ffffff;
            
            --bot-bubble-bg: #1e1e1e;
            --bot-text-color: #66b2ff; 
            
            --input-area-bg: rgba(30, 30, 30, 0.9);
            --input-box-bg: #2c2c2c;
            --input-border: #444;

            /* Vector Colors (Dark Mode) */
            --bot-outline: #81d4fa;
            --bot-face: #263238;
            --bot-body: #37474f;
            --bot-cheek: #ec407a;

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

        /* --- MAIN LAYOUT (Vertical Stack) --- */
        .app-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
        }

        /* --- HEADER --- */
        .header {
            padding: 10px 30px;
            border-bottom: 1px solid var(--border-color);
            display: flex; justify-content: space-between; align-items: center;
            background-color: var(--header-bg);
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
            z-index: 20;
            height: 110px;
        }
        
        .logo-img { height: 100px; width: auto; display: block; }
        .header-title { font-weight: bold; font-size: 24px; color: var(--text-color); margin-left: 15px;}
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

        /* --- CONTENT WRAPPER (Splits Left/Right) --- */
        .content-wrapper {
            display: flex;
            flex-direction: row; /* Side by side */
            flex: 1; /* Takes all available height */
            overflow: hidden; /* Prevent double scrollbars */
        }

        /* --- LEFT SIDEBAR (Description) --- */
        .sidebar {
            width: 35%; 
            min-width: 300px;
            max-width: 500px;
            background-color: transparent; 
            border-right: 1px solid var(--border-color);
            padding: 40px;
            
            /* Align to top so header is visible */
            display: flex;
            flex-direction: column;
            justify-content: flex-start; 
            
            /* Enable scrolling but hide the scrollbar */
            overflow-y: auto;
            scrollbar-width: none; /* Firefox */
        }
        .sidebar::-webkit-scrollbar { display: none; /* Chrome/Safari */ }

        .sidebar h2 {
            font-size: 24px;
            font-weight: 600;
            color: var(--text-color);
            opacity: 0.9;
            margin-bottom: 25px;
            margin-top: 10px;
            line-height: 1.4;
        }

        .sidebar ul {
            list-style-type: none;
            padding: 0;
        }

        .sidebar li {
            position: relative;
            padding-left: 20px;
            margin-bottom: 18px;
            line-height: 1.6;
            font-size: 18px;
        }

        .sidebar li::before {
            content: "•";
            color: var(--bot-text-color);
            font-weight: bold;
            font-size: 18px;
            position: absolute;
            left: 0;
            top: -2px;
        }


        /* --- RIGHT CHAT AREA (Just the messages) --- */
        .chat-container {
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            background: transparent;
            position: relative;
        }

        .chat-history {
            flex: 1; 
            padding: 20px 5%; 
            overflow-y: auto;
            display: flex; flex-direction: column; gap: 20px;
            background-color: transparent;
        }

        .message-row { display: flex; width: 100%; margin-bottom: 10px; }
        .message-row.user { justify-content: flex-end; }
        .message-row.bot { justify-content: flex-start; }

        /* --- BUBBLE FIX (Prevents explosion) --- */
        .message-bubble {
            max-width: 75%; 
            padding: 15px 25px; 
            border-radius: 12px;
            font-size: 16px; 
            line-height: 1.6; 
            position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            
            /* CRITICAL FIXES BELOW */
            overflow-wrap: break-word; /* Forces text to wrap */
            word-wrap: break-word;     /* Legacy support */
            min-width: 0;              /* Flexbox fix */
        }

        /* --- IMAGE FIX (Fits image to box) --- */
        .message-bubble img {
            max-width: 100% !important; /* Never wider than the bubble */
            height: auto !important;    /* Maintain aspect ratio */
            border-radius: 8px;
            margin-top: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: block;
        }

        /* --- TABLE FIX (Adds scrollbar if table is too big) --- */
        .message-bubble table {
            display: block;          /* Allows us to set overflow */
            width: 100%;             /* Fill the bubble */
            overflow-x: auto;        /* Adds a scrollbar ONLY if needed */
            margin: 15px 0;
            border-collapse: collapse;
        }

        /* Keep cells readable */
        .message-bubble th, .message-bubble td {
            white-space: nowrap;     /* Keeps data on one line (cleaner) */
            padding: 8px 12px;       /* Adds breathing room */
            border: 1px solid var(--border-color);
        }
        
        .message-bubble th { background-color: rgba(0,0,0,0.05); font-weight: bold; text-align: left; }

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

        /* --- VECTOR ICONS --- */
        .avatar-icon {
            width: 55px; height: 55px; 
            display: flex; align-items: center; justify-content: center;
            border-radius: 12px;
            margin: 0 15px; flex-shrink: 0;
            transition: all 0.3s ease;
            background: transparent; 
        }
        .user .avatar-icon { order: 2; margin-left: 15px; margin-right: 0; }
        .bot .avatar-icon { order: 1; margin-right: 15px; margin-left: 0; }
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

        /* Animations */
        @keyframes botFloat { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0px); } }
        .anim-bot-idle { animation: botFloat 3s ease-in-out infinite; }

        @keyframes userBreathe { 0% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-3px) scale(1.02); } 100% { transform: translateY(0px) scale(1); } }
        .anim-user-idle { animation: userBreathe 4.5s ease-in-out infinite; }

        @keyframes heartbeat { 0% { transform: scale(1); } 15% { transform: scale(1.1); } 30% { transform: scale(1); } 45% { transform: scale(1.1); } 60% { transform: scale(1); } 100% { transform: scale(1); } }
        @keyframes blink { 0%, 90%, 100% { transform: scaleY(1); } 95% { transform: scaleY(0.1); } }
        
        .anim-bot-thinking { animation: heartbeat 1.5s infinite ease-in-out; }
        .anim-bot-thinking .bot-eye { transform-origin: center; animation: blink 2s infinite; }

        /* --- REALISTIC LOADING ANIMATION --- */
        .loading-text {
            font-style: italic;
            color: var(--bot-text-color);
            opacity: 1;
            font-size: 0.95em;
            /* Smooth fade transition */
            transition: opacity 0.5s ease-in-out;
        }
        
        /* Fade out state */
        .loading-text.fade-out {
            opacity: 0;
        }
        
        /* Animated Dots */
        .loading-dots::after {
            content: ' .';
            animation: dots 1.5s steps(5, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: ' .'; }
            40% { content: ' ..'; }
            60% { content: ' ...'; }
            80%, 100% { content: ''; }
        }

        /* --- INPUT AREA (FULL WIDTH BOTTOM) --- */
        .input-area {
            padding: 20px;
            background-color: var(--input-area-bg);
            backdrop-filter: blur(10px);
            border-top: 1px solid var(--border-color);
            flex-shrink: 0;
            box-shadow: 0 -1px 3px rgba(0,0,0,0.05);
            
            /* Full width across bottom */
            width: 100%;
        }
        .input-box {
            display: flex; gap: 15px; width: 100%; max-width: 1200px;
            margin: 0 auto; align-items: center; 
        }
        input[type="text"] {
            flex: 1; padding: 12px 20px;
            border: 1px solid var(--input-border);
            border-radius: 8px; outline: none; font-size: 16px;
            background-color: var(--input-box-bg);
            color: var(--text-color);
            height: 50px; 
        }
        input[type="text"]:focus { border-color: #888; box-shadow: 0 0 0 2px rgba(0,0,0,0.05); }

        button.send-btn {
            background-color: #1f1f1f; border: none; border-radius: 10px;
            width: 50px; height: 50px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            padding: 0; flex-shrink: 0; transition: all 0.2s ease;
        }
        button.send-btn:hover { background-color: #000; transform: scale(1.05); }
        body.dark-mode button.send-btn { background-color: #ffffff; }
        body.dark-mode button.send-btn:hover { background-color: #e0e0e0; }
        button.send-btn svg { width: 22px; height: 22px; fill: white; margin-left: 2px; margin-top: 2px; }
        body.dark-mode button.send-btn svg { fill: #000000; }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            .header { height: 80px; }
            .logo-img { height: 60px; }
            .content-wrapper { flex-direction: column; }
            .sidebar { width: 100%; max-width: none; max-height: 25vh; border-right: none; border-bottom: 1px solid var(--border-color); padding: 15px; }
            .sidebar h2 { font-size: 18px; margin-bottom: 10px; }
            .sidebar li { font-size: 14px; margin-bottom: 8px; }
            .chat-container { height: 75vh; }
        }

    </style>
</head>
<body>

<div class="app-container">
    
    <div class="header">
        <div style="display: flex; align-items: center;">
            <img src="/static/multiquip.png" alt="Logo" class="logo-img" onerror="this.style.display='none'; document.getElementById('fallback-icon').style.display='block';">
            <span id="fallback-icon" style="display: none; font-size: 30px; margin-right: 10px;">🏗️</span>
        </div>
        
        <div class="header-controls">
            <button class="btn theme-btn" onclick="toggleTheme()" title="Toggle Dark Mode">
                <span id="theme-icon">🌙</span>
            </button>
            <button class="btn clear-btn" onclick="clearChat()">🗑️ Clear</button>
        </div>
    </div>

    <div class="content-wrapper">
        
        <div class="sidebar">
            <h2>Ask me About</h2>
            <ul>
                <li>Part Information for various models by providing the model number</li>
                <li>I can also answer look up parts based on common slangs</li>
                <li>I can display Images for various assembly drawings</li>
            </ul>
        </div>

        <div class="chat-container">
            <div class="chat-history" id="chat-box">
            </div>
        </div>

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
    
    // --- SESSION MANAGEMENT (NEW) ---
    // Generate a unique ID for this browser tab session
    let sessionId = sessionStorage.getItem('chatSessionId');
    if (!sessionId) {
        sessionId = 'sess-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        sessionStorage.setItem('chatSessionId', sessionId);
    }

    // --- CHAT LOGIC ---

    // Initialize first message
    window.onload = function() {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'message-row bot';
        rowDiv.innerHTML = `
            <div class="avatar-icon">${BOT_IDLE_HTML}</div>
            <div class="message-bubble"><p>Hello! Welcome to AskMQ. Please provide the model number of your MQ product, and I can provide parts information and images.</p></div>
        `;
        chatBox.appendChild(rowDiv);
    }

    function appendMessage(role, text, isHtml = false, animate = false) {
        const rowDiv = document.createElement('div');
        rowDiv.className = `message-row ${role}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar-icon';
        
        avatarDiv.innerHTML = role === 'user' ? USER_HTML : BOT_IDLE_HTML;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        rowDiv.appendChild(avatarDiv);
        rowDiv.appendChild(bubbleDiv);
        chatBox.appendChild(rowDiv);
        
        if (animate && role === 'bot') {
            let i = 0;
            const speed = 5; // Speed of typing
            
            function typeWriter() {
                if (i < text.length) {
                    i++;
                    const currentText = text.substring(0, i);
                    // Streaming Markdown
                    bubbleDiv.innerHTML = isHtml ? marked.parse(currentText) : currentText;
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                    setTimeout(typeWriter, speed);
                }
            }
            typeWriter();
        } else {
            // Instant render
            if (isHtml) {
                bubbleDiv.innerHTML = marked.parse(text); 
            } else {
                bubbleDiv.innerText = text;
            }
        }
        
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage(e) {
        e.preventDefault();
        const message = inputField.value.trim();
        if (!message) return;

        appendMessage('user', message, false, false);
        inputField.value = '';
        inputField.disabled = true;

        const loadingId = 'loading-' + Date.now();
        const loadingTextId = 'loading-text-' + Date.now();
        const loadingRow = document.createElement('div');
        loadingRow.className = 'message-row bot';
        loadingRow.id = loadingId;
        
        // --- REALISTIC AGENT ANIMATION START ---
        loadingRow.innerHTML = `
            <div class="avatar-icon">${BOT_THINKING_HTML}</div>
            <div class="message-bubble">
                <span id="${loadingTextId}" class="loading-text">AskMQ is looking for the requested Info<span class="loading-dots"></span></span>
            </div>
        `;
        chatBox.appendChild(loadingRow);
        chatBox.scrollTop = chatBox.scrollHeight;

        // --- ANIMATION STEP 2: Transition Text after 3.5 seconds ---
        const textSwitchTimer = setTimeout(() => {
            const textElement = document.getElementById(loadingTextId);
            if (textElement) {
                // 1. Fade Out
                textElement.classList.add('fade-out');
                
                // 2. Wait 0.5s for fade to finish, then Swap Text and Fade In
                setTimeout(() => {
                    textElement.innerHTML = `AskMQ is generating the response for you<span class="loading-dots"></span>`;
                    textElement.classList.remove('fade-out');
                }, 500); 
            }
        }, 3500);

        try {
            // SENDING SESSION_ID WITH REQUEST
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, session_id: sessionId })
            });
            const data = await response.json();
            
            // Stop animation logic
            clearTimeout(textSwitchTimer);
            document.getElementById(loadingId).remove();
            
            // Show actual response with typing effect
            appendMessage('bot', data.reply, true, true);
            
        } catch (error) {
            clearTimeout(textSwitchTimer);
            document.getElementById(loadingId).remove();
            appendMessage('bot', '⚠️ Error: Could not connect to the server.', false, false);
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
        
        // Optional: Reset Session ID to force new history on backend
        sessionId = 'sess-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        sessionStorage.setItem('chatSessionId', sessionId);
    }
</script>

</body>
</html>
"""

# ==========================================
# SERVER LOGIC (UPDATED WITH MEMORY)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_endpoint(payload: dict):
    user_message = payload.get("message", "")
    session_id = payload.get("session_id", "default_guest")

    # 1. Initialize memory if needed
    if session_id not in session_storage:
        session_storage[session_id] = deque(maxlen=10)
    
    # 2. Add User Message
    session_storage[session_id].append({"role": "user", "content": user_message})

    # 3. Send FULL HISTORY to Boomi
    full_history_payload = list(session_storage[session_id])

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BOOMI_URL,
                headers={"Content-Type": "application/json"},
                json=full_history_payload, # Sends the list of history
                auth=(BOOMI_USERNAME, BOOMI_PASSWORD),
                timeout=120.0
            )
            
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                bot_reply = data[0].get("content", "No content")
            elif isinstance(data, dict):
                bot_reply = data.get("content", "No content")
            else:
                bot_reply = "Empty response"
            
            # 4. Add Bot Reply to Memory
            session_storage[session_id].append({"role": "assistant", "content": bot_reply})
            
            return {"reply": bot_reply}
        else:
            # If error, remove the last user message so we don't confuse the AI next time
            session_storage[session_id].pop() 
            return {"reply": f"**Error {response.status_code}:** Unable to fetch data."}
            
    except httpx.RequestError as e:
        session_storage[session_id].pop() 
        return {"reply": f"**Connection Error:** {str(e)}"}
    except Exception as e:
        session_storage[session_id].pop() 
        return {"reply": f"**System Error:** {str(e)}"}

if os.path.exists("multiquip.png") or os.path.exists("multiquip_title.png"):
    app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

