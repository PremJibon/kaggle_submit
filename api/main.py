from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from security.auth import AuthService
from security.audit import AuditLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Personal Knowledge Assistant",
    description="Multi-agent system for organizing, retrieving, and synthesizing information",
    version="1.0.0"
)

security = HTTPBearer()
auth_service = AuthService()
audit_logger = AuditLogger()


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


HTML_INTERFACE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Personal Knowledge Assistant</title>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#333}
        .container{max-width:800px;margin:0 auto;padding:20px}
        header{background:#282c34;color:#fff;padding:20px;text-align:center;border-radius:8px 8px 0 0}
        h1{font-size:1.5rem}
        .card{background:#fff;padding:20px;margin-bottom:20px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,.1)}
        h2{color:#007bff;margin-bottom:15px;font-size:1.2rem}
        .form-group{margin-bottom:15px}
        label{display:block;margin-bottom:5px;font-weight:500;color:#555}
        input,textarea,select{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;font-size:1rem}
        textarea{min-height:80px;resize:vertical}
        button{background:#007bff;color:#fff;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-size:1rem}
        button:hover{background:#0056b3}
        .result{background:#f8f9fa;padding:15px;border-radius:4px;margin-top:15px;white-space:pre-wrap;font-family:monospace;font-size:.9rem;max-height:300px;overflow-y:auto}
        .success{border-left:4px solid #28a745}
        .error{border-left:4px solid #dc3545;color:#dc3545}
        .tabs{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
        .tab{padding:10px 20px;background:#e9ecef;border:none;border-radius:4px;cursor:pointer}
        .tab.active{background:#007bff;color:#fff}
        .hidden{display:none}
        .status{display:inline-block;padding:2px 8px;border-radius:3px;font-size:.8rem;background:#d4edda;color:#155724}
        .links{margin-top:15px}
        .links a{color:#007bff;text-decoration:none;margin-right:15px}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>AI Personal Knowledge Assistant</h1>
        <p style="margin-top:5px;opacity:.8">Multi-agent system powered by Google ADK</p>
    </header>
    <div class="card">
        <h2>System Status</h2>
        <p>Status: <span class="status">Running</span></p>
        <div class="links">
            <a href="/docs" target="_blank">API Docs</a>
            <a href="/redoc" target="_blank">ReDoc</a>
            <a href="/health" target="_blank">Health</a>
        </div>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="showTab('register',this)">Register</button>
        <button class="tab" onclick="showTab('login',this)">Login</button>
        <button class="tab" onclick="showTab('chat',this)">Chat with Agent</button>
    </div>
    <div id="register" class="card">
        <h2>Register</h2>
        <div class="form-group"><label>Username</label><input type="text" id="reg-username"></div>
        <div class="form-group"><label>Email</label><input type="email" id="reg-email"></div>
        <div class="form-group"><label>Password</label><input type="password" id="reg-password"></div>
        <button onclick="doRegister()">Register</button>
        <div id="reg-result" class="result hidden"></div>
    </div>
    <div id="login" class="card hidden">
        <h2>Login</h2>
        <div class="form-group"><label>Username</label><input type="text" id="login-username"></div>
        <div class="form-group"><label>Password</label><input type="password" id="login-password"></div>
        <button onclick="doLogin()">Login</button>
        <div id="login-result" class="result hidden"></div>
    </div>
    <div id="chat" class="card hidden">
        <h2>Chat with Knowledge Assistant</h2>
        <p style="margin-bottom:15px;color:#666">Ask the agent to add notes, search, summarize, or organize your knowledge.</p>
        <div class="form-group"><label>Your Message</label><textarea id="chat-input" placeholder="e.g. Add a note about my meeting today..."></textarea></div>
        <button onclick="sendChat()">Send</button>
        <div id="chat-result" class="result hidden"></div>
    </div>
</div>
<script>
let token=localStorage.getItem('token');
function showTab(id,btn){document.querySelectorAll('.card').forEach(c=>c.classList.add('hidden'));document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.getElementById(id).classList.remove('hidden');if(btn)btn.classList.add('active')}
async function api(url,method,body){const h={'Content-Type':'application/json'};if(token)h['Authorization']='Bearer '+token;const o={method,headers:h};if(body)o.body=JSON.stringify(body);const r=await fetch(url,o);return await r.json()}
function show(el,d,err){const e=document.getElementById(el);e.classList.remove('hidden','success','error');e.classList.add(err?'error':'success');e.textContent=JSON.stringify(d,null,2)}
async function doRegister(){try{const d=await api('/auth/register','POST',{username:document.getElementById('reg-username').value,email:document.getElementById('reg-email').value,password:document.getElementById('reg-password').value});show('reg-result',d)}catch(e){show('reg-result',{error:e.message},true)}}
async function doLogin(){try{const d=await api('/auth/login','POST',{username:document.getElementById('login-username').value,password:document.getElementById('login-password').value});show('login-result',d);if(d.access_token){token=d.access_token;localStorage.setItem('token',token)}}catch(e){show('login-result',{error:e.message},true)}}
async function sendChat(){try{const d=await api('/chat','POST',{message:document.getElementById('chat-input').value});show('chat-result',d)}catch(e){show('chat-result',{error:e.message},true)}}
</script>
</body>
</html>"""


@app.on_event("startup")
async def startup():
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shut down")


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_INTERFACE


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "adk_version": "2.2.0",
    }


@app.post("/auth/register")
async def register(user_data: UserRegister):
    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    audit_logger.log_user_action(user_id=user.id, action="register", resource="user")
    return {"message": "User registered", "user_id": user.id, "username": user.username}


@app.post("/auth/login")
async def login(user_data: UserLogin):
    user = auth_service.authenticate_user(username=user_data.username, password=user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth_service.create_access_token(data={"sub": user.id})
    audit_logger.log_user_action(user_id=user.id, action="login", resource="user")
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username}


@app.post("/chat")
async def chat(body: dict, user=Depends(get_current_user)):
    message = body.get("message", "")
    audit_logger.log_user_action(user_id=user.id, action="chat", resource="agent", details={"message": message[:100]})
    return {
        "status": "success",
        "message": f"Received: {message}. To chat with the agent, run: cd knowledge_agent && adk web",
        "hint": "The ADK agent can be started with 'adk web' from the knowledge_agent/ directory.",
    }