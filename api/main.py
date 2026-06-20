from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from agents.coordinator import AgentCoordinator
from mcp_servers.knowledge_mcp_server import KnowledgeMCPServer
from security.auth import AuthService
from security.encryption import EncryptionService
from security.audit import AuditLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Personal Knowledge Assistant",
    description="Multi-agent system for organizing, retrieving, and synthesizing information",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Initialize services
agent_coordinator = AgentCoordinator()
mcp_server = KnowledgeMCPServer()
auth_service = AuthService()
encryption_service = EncryptionService()
audit_logger = AuditLogger()


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class ItemCreate(BaseModel):
    content: str
    source_type: str = "manual"
    source_url: str = ""
    format: str = "text"


class SearchQuery(BaseModel):
    query: str
    max_results: int = 10


class SynthesisRequest(BaseModel):
    items: List[Dict[str, Any]]
    synthesis_type: str = "summary"


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    await agent_coordinator.initialize()
    await mcp_server.initialize()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Clean up services on shutdown."""
    await agent_coordinator.cleanup()
    await mcp_server.cleanup()
    logger.info("Application shut down")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Personal Knowledge Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        header { background: #282c34; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        h1 { font-size: 1.5rem; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { color: #007bff; margin-bottom: 15px; font-size: 1.2rem; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; color: #555; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        textarea { min-height: 80px; resize: vertical; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        button:hover { background: #0056b3; }
        button.secondary { background: #6c757d; }
        button.secondary:hover { background: #545b62; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; max-height: 300px; overflow-y: auto; }
        .success { border-left: 4px solid #28a745; }
        .error { border-left: 4px solid #dc3545; color: #dc3545; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #e9ecef; border: none; border-radius: 4px; cursor: pointer; }
        .tab.active { background: #007bff; color: white; }
        .hidden { display: none; }
        .status { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.8rem; }
        .status.running { background: #d4edda; color: #155724; }
        .links { margin-top: 15px; }
        .links a { color: #007bff; text-decoration: none; margin-right: 15px; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Personal Knowledge Assistant</h1>
            <p style="margin-top: 5px; opacity: 0.8;">Multi-agent system for organizing, retrieving, and synthesizing information</p>
        </header>
        
        <div class="card">
            <h2>System Status</h2>
            <p>Status: <span class="status running">Running</span></p>
            <div class="links">
                <a href="/docs" target="_blank">API Documentation</a>
                <a href="/redoc" target="_blank">ReDoc</a>
                <a href="/health" target="_blank">Health Check</a>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('register')">Register</button>
            <button class="tab" onclick="showTab('login')">Login</button>
            <button class="tab" onclick="showTab('items')">Add Item</button>
            <button class="tab" onclick="showTab('search')">Search</button>
            <button class="tab" onclick="showTab('sync')">Sync Sources</button>
        </div>
        
        <div id="register" class="card">
            <h2>Register New User</h2>
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="reg-username" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="reg-email" placeholder="Enter email">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="reg-password" placeholder="Enter password">
            </div>
            <button onclick="register()">Register</button>
            <div id="reg-result" class="result hidden"></div>
        </div>
        
        <div id="login" class="card hidden">
            <h2>Login</h2>
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="login-username" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="login-password" placeholder="Enter password">
            </div>
            <button onclick="login()">Login</button>
            <div id="login-result" class="result hidden"></div>
        </div>
        
        <div id="items" class="card hidden">
            <h2>Add New Item</h2>
            <div class="form-group">
                <label>Content</label>
                <textarea id="item-content" placeholder="Enter your note, idea, or information..."></textarea>
            </div>
            <div class="form-group">
                <label>Source Type</label>
                <select id="item-source">
                    <option value="manual">Manual Entry</option>
                    <option value="google_keep">Google Keep</option>
                    <option value="google_drive">Google Drive</option>
                    <option value="browser">Browser</option>
                </select>
            </div>
            <button onclick="addItem()">Add Item</button>
            <div id="item-result" class="result hidden"></div>
        </div>
        
        <div id="search" class="card hidden">
            <h2>Search Knowledge Base</h2>
            <div class="form-group">
                <label>Search Query</label>
                <input type="text" id="search-query" placeholder="Search for notes, ideas, information...">
            </div>
            <button onclick="searchKnowledge()">Search</button>
            <div id="search-result" class="result hidden"></div>
        </div>
        
        <div id="sync" class="card hidden">
            <h2>Sync Sources</h2>
            <p>Sync content from all connected sources (Google Keep, Google Drive, Browser)</p>
            <br>
            <button onclick="syncSources()">Sync All Sources</button>
            <div id="sync-result" class="result hidden"></div>
        </div>
    </div>
    
    <script>
        let token = localStorage.getItem('token');
        
        function showTab(tabId) {
            document.querySelectorAll('.card').forEach(c => c.classList.add('hidden'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabId).classList.remove('hidden');
            event.target.classList.add('active');
        }
        
        async function apiCall(url, method = 'GET', body = null) {
            const headers = {'Content-Type': 'application/json'};
            if (token) headers['Authorization'] = 'Bearer ' + token;
            const opts = {method, headers};
            if (body) opts.body = JSON.stringify(body);
            const res = await fetch(url, opts);
            return await res.json();
        }
        
        function showResult(elementId, data, isError = false) {
            const el = document.getElementById(elementId);
            el.classList.remove('hidden', 'success', 'error');
            el.classList.add(isError ? 'error' : 'success');
            el.textContent = JSON.stringify(data, null, 2);
        }
        
        async function register() {
            try {
                const data = await apiCall('/auth/register', 'POST', {
                    username: document.getElementById('reg-username').value,
                    email: document.getElementById('reg-email').value,
                    password: document.getElementById('reg-password').value
                });
                showResult('reg-result', data);
                if (data.access_token) {
                    token = data.access_token;
                    localStorage.setItem('token', token);
                }
            } catch(e) { showResult('reg-result', {error: e.message}, true); }
        }
        
        async function login() {
            try {
                const data = await apiCall('/auth/login', 'POST', {
                    username: document.getElementById('login-username').value,
                    password: document.getElementById('login-password').value
                });
                showResult('login-result', data);
                if (data.access_token) {
                    token = data.access_token;
                    localStorage.setItem('token', token);
                }
            } catch(e) { showResult('login-result', {error: e.message}, true); }
        }
        
        async function addItem() {
            try {
                const data = await apiCall('/items', 'POST', {
                    content: document.getElementById('item-content').value,
                    source_type: document.getElementById('item-source').value
                });
                showResult('item-result', data);
            } catch(e) { showResult('item-result', {error: e.message}, true); }
        }
        
        async function searchKnowledge() {
            try {
                const data = await apiCall('/search', 'POST', {
                    query: document.getElementById('search-query').value,
                    max_results: 10
                });
                showResult('search-result', data);
            } catch(e) { showResult('search-result', {error: e.message}, true); }
        }
        
        async function syncSources() {
            try {
                const data = await apiCall('/sync');
                showResult('sync-result', data);
            } catch(e) { showResult('sync-result', {error: e.message}, true); }
        }
        
        // Show login tab by default if no token
        if (!token) showTab('register');
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML interface."""
    return HTML_INTERFACE


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": agent_coordinator.get_agent_status()
    }


@app.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user."""
    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="register",
        resource="user"
    )
    
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username
    }


@app.post("/auth/login")
async def login(user_data: UserLogin):
    """Login a user."""
    user = auth_service.authenticate_user(
        username=user_data.username,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id}
    )
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="login",
        resource="user"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }


@app.post("/items")
async def create_item(item: ItemCreate, user = Depends(get_current_user)):
    """Create a new item and process it through the agent pipeline."""
    # Process item through agent coordinator
    result = await agent_coordinator.process_item({
        "content": item.content,
        "source_type": item.source_type,
        "source_url": item.source_url,
        "format": item.format
    })
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="create_item",
        resource="item",
        details={"item_id": result.get("knowledge_item", {}).get("id")}
    )
    
    return result


@app.post("/search")
async def search_knowledge(query: SearchQuery, user = Depends(get_current_user)):
    """Search the knowledge base."""
    result = await agent_coordinator.search_knowledge(
        query=query.query,
        max_results=query.max_results
    )
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="search",
        resource="knowledge_base",
        details={"query": query.query, "results_count": result.get("total_results", 0)}
    )
    
    return result


@app.post("/synthesize")
async def synthesize_information(request: SynthesisRequest, user = Depends(get_current_user)):
    """Synthesize information from multiple items."""
    result = await agent_coordinator.synthesize_information(
        items=request.items,
        synthesis_type=request.synthesis_type
    )
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="synthesize",
        resource="knowledge_base",
        details={"synthesis_type": request.synthesis_type, "input_count": len(request.items)}
    )
    
    return result


@app.get("/sync")
async def sync_sources(user = Depends(get_current_user)):
    """Sync content from all connected sources."""
    result = await mcp_server.sync_all()
    
    # Log the event
    audit_logger.log_user_action(
        user_id=user.id,
        action="sync",
        resource="mcp_server",
        details={"total_items": result.get("total_items", 0)}
    )
    
    return result


@app.get("/sources")
async def get_sources(user = Depends(get_current_user)):
    """Get available sources."""
    return mcp_server.get_source_status()


@app.get("/audit")
async def get_audit_logs(user = Depends(get_current_user), limit: int = 100):
    """Get audit logs (admin only)."""
    # In a real app, check if user is admin
    return audit_logger.get_events(limit=limit)


@app.get("/agent-status")
async def get_agent_status(user = Depends(get_current_user)):
    """Get status of all agents."""
    return agent_coordinator.get_agent_status()