from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import re

from security.auth import AuthService
from security.audit import AuditLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Personal Knowledge Assistant", version="2.0.0")
security = HTTPBearer()
auth_service = AuthService()
audit_logger = AuditLogger()
knowledge_base: list = []


class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def process_chat(message: str, user_id: str) -> dict:
    msg = message.lower().strip()

    if any(w in msg for w in ["add note", "new note", "create note", "save note", "add a note"]):
        title_match = re.search(r'(?:about|for|titled?|called)?\s*["\']?(.+?)["\']?\s*$', message, re.I)
        title = title_match.group(1).strip() if title_match else message.replace("add note", "").replace("new note", "").strip()
        if not title:
            title = "Untitled Note"
        item = {"id": f"n{len(knowledge_base)+1}", "type": "note", "title": title.title(), "content": title, "tags": ["note"], "created_at": datetime.now().isoformat()}
        knowledge_base.append(item)
        return {"type": "note_added", "message": f"Note added: {title.title()}", "item": item}

    if any(w in msg for w in ["add bookmark", "save bookmark", "bookmark", "add url"]):
        url_match = re.search(r'(https?://\S+)', message)
        url = url_match.group(1) if url_match else "https://example.com"
        title = message.replace("add bookmark", "").replace("save bookmark", "").replace(url, "").strip() or "My Bookmark"
        item = {"id": f"b{len(knowledge_base)+1}", "type": "bookmark", "title": title.title(), "url": url, "content": url, "tags": ["bookmark"], "created_at": datetime.now().isoformat()}
        knowledge_base.append(item)
        return {"type": "bookmark_added", "message": f"Bookmark saved: {title.title()}", "item": item}

    if any(w in msg for w in ["search", "find", "look for", "where is"]):
        query = message
        for w in ["search for ", "search ", "find ", "look for ", "where is "]:
            query = query.replace(w, "")
        query = query.strip()
        if not query:
            query = message
        results = []
        query_lower = query.lower()
        for item in knowledge_base:
            searchable = f"{item.get('title','')} {item.get('content','')} {item.get('url','')} {' '.join(item.get('tags',[]))}".lower()
            score = 0
            if query_lower in searchable:
                score = searchable.count(query_lower)
            else:
                for word in query_lower.split():
                    if len(word) > 2 and word in searchable:
                        score += 1
            if score > 0:
                results.append({**item, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        if results:
            return {"type": "search_results", "message": f"Found {len(results)} results for '{query}'", "results": results}
        return {"type": "no_results", "message": f"No results found for '{query}'. Try different keywords."}

    if any(w in msg for w in ["summarize", "summary", "sum up", "overview"]):
        if not knowledge_base:
            return {"type": "empty", "message": "No items to summarize yet. Add some notes first!"}
        notes = [i for i in knowledge_base if i["type"] == "note"]
        bookmarks = [i for i in knowledge_base if i["type"] == "bookmark"]
        all_tags = set()
        for item in knowledge_base:
            all_tags.update(item.get("tags", []))
        return {"type": "summary", "message": f"Knowledge Base Summary", "stats": {"total": len(knowledge_base), "notes": len(notes), "bookmarks": len(bookmarks), "tags": list(all_tags)[:10]}}

    if any(w in msg for w in ["connect", "connection", "related"]):
        connections = []
        for i in range(len(knowledge_base)):
            for j in range(i+1, len(knowledge_base)):
                common = set(knowledge_base[i].get("tags",[])).intersection(set(knowledge_base[j].get("tags",[])))
                if common:
                    connections.append({"from": knowledge_base[i]["title"], "to": knowledge_base[j]["title"], "shared": list(common)})
        if connections:
            return {"type": "connections", "message": f"Found {len(connections)} connections", "connections": connections}
        return {"type": "no_connections", "message": "No connections found yet. Add more items with similar tags!"}

    if any(w in msg for w in ["categorize", "category", "classify", "organize"]):
        categories = {"work": ["meeting","project","deadline","client"], "learning": ["course","tutorial","research","study"], "ideas": ["idea","brainstorm","concept"], "reference": ["doc","guide","manual"]}
        results = []
        for item in knowledge_base:
            content = f"{item.get('title','')} {item.get('content','')}".lower()
            for cat, kws in categories.items():
                if any(k in content for k in kws):
                    results.append({"title": item["title"], "category": cat})
                    break
        if results:
            return {"type": "categories", "message": f"Categorized {len(results)} items", "categories": results}
        return {"type": "no_categories", "message": "Not enough items to categorize yet."}

    if any(w in msg for w in ["list", "show all", "show me", "what do i have", "my items"]):
        if not knowledge_base:
            return {"type": "empty", "message": "Your knowledge base is empty. Add some notes!"}
        return {"type": "list_items", "message": f"You have {len(knowledge_base)} items", "items": knowledge_base[-10:]}

    if any(w in msg for w in ["delete", "remove"]):
        title_match = re.search(r'(?:delete|remove)\s+(.+)', message, re.I)
        if title_match:
            title = title_match.group(1).strip()
            for i, item in enumerate(knowledge_base):
                if title.lower() in item.get("title","").lower():
                    removed = knowledge_base.pop(i)
                    return {"type": "deleted", "message": f"Deleted: {removed['title']}"}
            return {"type": "not_found", "message": f"Could not find '{title}' to delete."}
        return {"type": "clarify", "message": "What would you like to delete? Provide the item title."}

    if any(w in msg for w in ["help", "what can you do", "commands", "options"]):
        return {"type": "help", "message": "Here's what I can do:", "commands": [
            {"cmd": "Add note about [topic]", "desc": "Create a new note"},
            {"cmd": "Add bookmark [url]", "desc": "Save a bookmark"},
            {"cmd": "Search [query]", "desc": "Find items in your knowledge base"},
            {"cmd": "Summarize", "desc": "Get an overview of your items"},
            {"cmd": "Connect", "desc": "Find connections between items"},
            {"cmd": "Categorize", "desc": "Auto-organize your items"},
            {"cmd": "List", "desc": "Show all items"},
            {"cmd": "Delete [title]", "desc": "Remove an item"},
        ]}

    return {"type": "chat", "message": f"I received your message. Try commands like:\n- 'Add note about my meeting'\n- 'Search for meeting'\n- 'Summarize'\n- 'Help'"}


@app.on_event("startup")
async def startup():
    logger.info("App started")


@app.get("/", response_class=HTMLResponse)
async def root():
    return PAGE


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/auth/register")
async def register(body: UserRegister):
    user = auth_service.create_user(body.username, body.email, body.password)
    audit_logger.log_user_action(user_id=user.id, action="register", resource="user")
    return {"message": "Account created", "user_id": user.id, "username": user.username}


@app.post("/auth/login")
async def login(body: UserLogin):
    user = auth_service.authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token_val = auth_service.create_access_token({"sub": user.id})
    return {"access_token": token_val, "token_type": "bearer", "user_id": user.id, "username": user.username}


@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username}


@app.get("/items")
async def list_items(user=Depends(get_current_user)):
    return {"items": knowledge_base, "total": len(knowledge_base)}


@app.post("/chat")
async def chat(body: ChatRequest, user=Depends(get_current_user)):
    result = process_chat(body.message, user.id)
    audit_logger.log_user_action(user_id=user.id, action="chat", resource="agent", details={"message": body.message[:50]})
    return result


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Knowledge Assistant</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0a;--surface:#141414;--surface2:#1a1a1a;--border:#262626;--primary:#3b82f6;--accent:#10b981;--text:#fafafa;--muted:#737373;--danger:#ef4444;--warning:#f59e0b}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
.font-display{font-family:'Instrument Serif',serif}
.app{max-width:860px;margin:0 auto;padding:16px}
header{text-align:center;padding:32px 0 24px}
header h1{font-size:clamp(1.8rem,5vw,2.8rem);font-family:'Instrument Serif',serif;font-style:italic;background:linear-gradient(135deg,#89AACC,#4E85BF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
header p{color:var(--muted);font-size:.9rem}
.nav{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}
.nav button{padding:8px 16px;border:1px solid var(--border);background:transparent;color:var(--muted);border-radius:999px;cursor:pointer;font-size:.8rem;transition:all .2s;font-family:inherit}
.nav button:hover{color:var(--text);border-color:var(--muted)}
.nav button.active{background:var(--text);color:var(--bg);border-color:var(--text)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:16px}
.card h2{font-size:1.1rem;font-family:'Instrument Serif',serif;font-style:italic;margin-bottom:14px;color:var(--text)}
.input-group{display:flex;gap:8px;margin-bottom:12px}
.input-group input,.input-group textarea{flex:1;padding:12px 14px;border:1px solid var(--border);border-radius:10px;font-size:.9rem;background:var(--bg);color:var(--text);font-family:inherit;outline:none;transition:border .2s}
.input-group input:focus,.input-group textarea:focus{border-color:var(--primary)}
.input-group textarea{min-height:80px;resize:vertical}
.btn{padding:10px 20px;border:none;border-radius:10px;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .15s;font-family:inherit;white-space:nowrap}
.btn-p{background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff}
.btn-p:hover{opacity:.9;transform:scale(1.02)}
.btn-s{background:var(--surface2);color:var(--text);border:1px solid var(--border)}
.btn-s:hover{border-color:var(--muted)}
.btn-d{background:var(--danger);color:#fff;font-size:.75rem;padding:4px 10px}
.msg{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;margin-top:12px;font-size:.85rem;white-space:pre-wrap;line-height:1.6;max-height:300px;overflow-y:auto}
.msg.ok{border-left:3px solid var(--accent)}
.msg.err{border-left:3px solid var(--danger);color:var(--danger)}
.hidden{display:none}
.item{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;transition:border .2s}
.item:hover{border-color:var(--primary)}
.item .info{flex:1;min-width:0}
.item .title{font-weight:600;font-size:.9rem;margin-bottom:4px}
.item .content{color:var(--muted);font-size:.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.item .tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:.7rem;font-weight:500;background:rgba(59,130,246,.12);color:var(--primary)}
.badge.g{background:rgba(16,185,129,.12);color:var(--accent)}
.badge.y{background:rgba(245,158,11,.12);color:var(--warning)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px}
.stat{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center}
.stat .n{font-size:1.6rem;font-weight:700;background:linear-gradient(135deg,#89AACC,#4E85BF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat .l{color:var(--muted);font-size:.7rem;margin-top:2px}
.guide{display:flex;gap:12px;align-items:flex-start;padding:12px;background:var(--bg);border-radius:10px;border:1px solid var(--border);margin-bottom:10px}
.guide .num{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;flex-shrink:0}
.guide .text h4{font-size:.85rem;margin-bottom:2px}
.guide .text p{color:var(--muted);font-size:.8rem}
.cmd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px}
.cmd{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 10px;cursor:pointer;transition:all .15s}
.cmd:hover{border-color:var(--primary);background:var(--surface2)}
.cmd .c{font-size:.8rem;font-weight:500;color:var(--text)}
.cmd .d{font-size:.7rem;color:var(--muted)}
.chat-box{position:relative}
.chat-box textarea{width:100%;padding:14px 100px 14px 14px;border:1px solid var(--border);border-radius:12px;font-size:.9rem;background:var(--bg);color:var(--text);font-family:inherit;outline:none;resize:none;min-height:52px;max-height:120px;transition:border .2s}
.chat-box textarea:focus{border-color:var(--primary)}
.chat-box .send{position:absolute;right:8px;bottom:8px;padding:8px 16px}
.chat-history{max-height:500px;overflow-y:auto;margin-bottom:12px;padding-right:4px}
.chat-history::-webkit-scrollbar{width:4px}
.chat-history::-webkit-scrollbar-track{background:transparent}
.chat-history::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.chat-msg{margin-bottom:10px;animation:fadeIn .2s}
.chat-msg.user{text-align:right}
.chat-msg .bubble{display:inline-block;max-width:80%;padding:10px 14px;border-radius:12px;font-size:.85rem;line-height:1.5;text-align:left}
.chat-msg.user .bubble{background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff;border-bottom-right-radius:4px}
.chat-msg.bot .bubble{background:var(--surface2);border:1px solid var(--border);border-bottom-left-radius:4px}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:600px){.stats{grid-template-columns:repeat(2,1fr)}.cmd-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="app" id="app"></div>
<script>
let T=localStorage.getItem('tk'),U=null,items=[],tab='chat',chatHist=[];
const api=async(u,m='GET',b=null)=>{const h={'Content-Type':'application/json'};if(T)h['Authorization']='Bearer '+T;const o={method:m,headers:h};if(b)o.body=JSON.stringify(b);const r=await fetch(u,o);if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||'Error')}return r.json()};
const $(id)=>document.getElementById(id);
const v=(id)=>$(id)?.value?.trim()||'';

function render(){
  if(!T){renderAuth();return}
  renderApp();
}

function renderAuth(){
  const isReg=tab==='reg';
  $('app').innerHTML=`
  <header><h1>AI Knowledge Assistant</h1><p>Organize, search & synthesize your knowledge</p></header>
  <div class="card">
    <div class="nav"><button class="${isReg?'active':''}" onclick="tab='reg';render()">Register</button><button class="${!isReg?'active':''}" onclick="tab='login';render()">Login</button></div>
    ${isReg?`
      <div class="input-group"><input id="r-u" placeholder="Username"></div>
      <div class="input-group"><input id="r-e" type="email" placeholder="Email"></div>
      <div class="input-group"><input id="r-p" type="password" placeholder="Password"></div>
      <button class="btn btn-p" onclick="doReg()" style="width:100%">Create Account</button>
    `:`
      <div class="input-group"><input id="l-u" placeholder="Username"></div>
      <div class="input-group"><input id="l-p" type="password" placeholder="Password"></div>
      <button class="btn btn-p" onclick="doLogin()" style="width:100%">Sign In</button>
    `}
    <div id="amsg" class="msg hidden" style="margin-top:12px"></div>
  </div>
  <div class="card"><h2>Getting Started</h2>
    <div class="guide"><div class="num">1</div><div class="text"><h4>Create Account</h4><p>Register with any username, email, and password</p></div></div>
    <div class="guide"><div class="num">2</div><div class="text"><h4>Chat Commands</h4><p>Type natural commands like "add note about meeting" or "search for project"</p></div></div>
    <div class="guide"><div class="num">3</div><div class="text"><h4>Browse & Search</h4><p>Use the Browse tab to see all items and filter by tags</p></div></div>
  </div>`;
}

function renderApp(){
  $('app').innerHTML=`
  <header>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div><h1>Knowledge Assistant</h1><p style="color:var(--muted);font-size:.85rem">Welcome, <span style="color:var(--accent)">${U?.username||'User'}</span></p></div>
      <button class="btn btn-s" onclick="logout()" style="font-size:.75rem;padding:6px 12px">Logout</button>
    </div>
  </header>
  <div class="stats">
    <div class="stat"><div class="n">${items.length}</div><div class="l">Total Items</div></div>
    <div class="stat"><div class="n">${items.filter(i=>i.type==='note').length}</div><div class="l">Notes</div></div>
    <div class="stat"><div class="n">${items.filter(i=>i.type==='bookmark').length}</div><div class="l">Bookmarks</div></div>
    <div class="stat"><div class="n">${new Set(items.flatMap(i=>i.tags||[])).size}</div><div class="l">Tags</div></div>
  </div>
  <div class="nav">
    <button class="${tab==='chat'?'active':''}" onclick="tab='chat';render()">Chat</button>
    <button class="${tab==='browse'?'active':''}" onclick="tab='browse';render()">Browse</button>
    <button class="${tab==='guide'?'active':''}" onclick="tab='guide';render()">Guide</button>
  </div>
  <div id="ct"></div>`;
  renderTab();
}

function renderTab(){
  const c=$('ct');if(!c)return;
  if(tab==='chat')renderChat(c);
  else if(tab==='browse')renderBrowse(c);
  else if(tab==='guide')renderGuide(c);
}

function renderChat(c){
  c.innerHTML=`
  <div class="card">
    <h2>Chat with Assistant</h2>
    <div class="chat-history" id="ch">${chatHist.map(m=>`<div class="chat-msg ${m.role}"><div class="bubble">${m.text.replace(/\\n/g,'<br>')}</div></div>`).join('')}</div>
    <div class="chat-box">
      <textarea id="ci" placeholder="Try: add note about meeting, search for project, summarize..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChat()}"></textarea>
      <button class="btn btn-p send" onclick="sendChat()">Send</button>
    </div>
  </div>
  <div class="card"><h2>Quick Commands</h2><div class="cmd-grid">
    <div class="cmd" onclick="quickChat('Add note about my meeting today')"><div class="c">Add note</div><div class="d">Create a new note</div></div>
    <div class="cmd" onclick="quickChat('Add bookmark https://google.com Google')"><div class="c">Add bookmark</div><div class="d">Save a URL</div></div>
    <div class="cmd" onclick="quickChat('Search for note')"><div class="c">Search</div><div class="d">Find items</div></div>
    <div class="cmd" onclick="quickChat('Summarize')"><div class="c">Summarize</div><div class="d">Overview of items</div></div>
    <div class="cmd" onclick="quickChat('List all items')"><div class="c">List items</div><div class="d">Show everything</div></div>
    <div class="cmd" onclick="quickChat('Find connections')"><div class="c">Connections</div><div class="d">Related items</div></div>
    <div class="cmd" onclick="quickChat('Categorize items')"><div class="c">Categorize</div><div class="d">Auto-organize</div></div>
    <div class="cmd" onclick="quickChat('Help')"><div class="c">Help</div><div class="d">Show commands</div></div>
  </div></div>`;
  const ch=$('ch');if(ch)ch.scrollTop=ch.scrollHeight;
}

function renderBrowse(c){
  const tags=[...new Set(items.flatMap(i=>i.tags||[]))];
  c.innerHTML=`
  <div class="card">
    <h2>Browse Items</h2>
    <div class="input-group" style="margin-bottom:12px">
      <select id="ft" onchange="filterItems()" style="flex:1;padding:10px;border:1px solid var(--border);border-radius:10px;background:var(--bg);color:var(--text);font-size:.85rem">
        <option value="">All Tags</option>
        ${tags.map(t=>`<option value="${t}">${t}</option>`).join('')}
      </select>
    </div>
    <div id="il"></div>
  </div>`;
  filterItems();
}

function filterItems(){
  const tag=v('ft');
  const filtered=tag?items.filter(i=>(i.tags||[]).includes(tag)):items;
  const el=$('il');if(!el)return;
  el.innerHTML=filtered.length===0?'<p style="color:var(--muted);text-align:center;padding:24px">No items yet</p>':
    filtered.map(i=>`<div class="item"><div class="info"><div class="title">${i.title||'Untitled'}</div><div class="content">${(i.content||i.url||'').substring(0,120)}</div><div class="tags">${(i.tags||[]).map(t=>`<span class="badge">${t}</span>`).join('')}<span class="badge ${i.type==='bookmark'?'y':'g'}">${i.type}</span></div></div><button class="btn btn-d" onclick="deleteItem('${i.id}')">X</button></div>`).join('');
}

function renderGuide(c){
  c.innerHTML=`
  <div class="card"><h2>How to Use</h2>
    <div class="guide"><div class="num">1</div><div class="text"><h4>Add Notes</h4><p>Type "add note about [topic]" in the chat to save ideas, meeting notes, or research.</p></div></div>
    <div class="guide"><div class="num">2</div><div class="text"><h4>Save Bookmarks</h4><p>Type "add bookmark [url] [title]" to save important links.</p></div></div>
    <div class="guide"><div class="num">3</div><div class="text"><h4>Search Everything</h4><p>Type "search for [keyword]" to find notes and bookmarks instantly.</p></div></div>
    <div class="guide"><div class="num">4</div><div class="text"><h4>Get Summaries</h4><p>Type "summarize" to see an overview of your knowledge base.</p></div></div>
    <div class="guide"><div class="num">5</div><div class="text"><h4>Find Connections</h4><p>Type "find connections" to discover related items by tags.</p></div></div>
    <div class="guide"><div class="num">6</div><div class="text"><h4>Categorize</h4><p>Type "categorize items" to auto-organize your content.</p></div></div>
  </div>
  <div class="card"><h2>Commands Reference</h2><div class="cmd-grid">
    <div class="cmd" onclick="quickChat('Add note about my meeting')"><div class="c">Add note about [topic]</div><div class="d">Create note</div></div>
    <div class="cmd" onclick="quickChat('Add bookmark https://example.com Example')"><div class="c">Add bookmark [url]</div><div class="d">Save bookmark</div></div>
    <div class="cmd" onclick="quickChat('Search for meeting')"><div class="c">Search [query]</div><div class="d">Find items</div></div>
    <div class="cmd" onclick="quickChat('Summarize')"><div class="c">Summarize</div><div class="d">Get overview</div></div>
    <div class="cmd" onclick="quickChat('List all items')"><div class="c">List</div><div class="d">Show all items</div></div>
    <div class="cmd" onclick="quickChat('Find connections')"><div class="c">Find connections</div><div class="d">Related items</div></div>
    <div class="cmd" onclick="quickChat('Categorize items')"><div class="c">Categorize</div><div class="d">Auto-organize</div></div>
    <div class="cmd" onclick="quickChat('Delete [title]')"><div class="c">Delete [title]</div><div class="d">Remove item</div></div>
  </div></div>`;
}

async function sendChat(){
  const input=$('ci');if(!input)return;
  const msg=input.value.trim();if(!msg)return;
  input.value='';
  chatHist.push({role:'user',text:msg});
  renderChat($('ct'));
  try{
    const d=await api('/chat','POST',{message:msg});
    let resp=d.message;
    if(d.type==='search_results'&&d.results){
      resp+='\\n\\n'+d.results.map(r=>`  - ${r.title} (${r.type})`).join('\\n');
    }
    if(d.type==='summary'&&d.stats){
      resp+='\\n\\nNotes: '+d.stats.notes+' | Bookmarks: '+d.stats.bookmarks+'\\nTags: '+d.stats.tags.join(', ');
    }
    if(d.type==='connections'&&d.connections){
      resp+='\\n\\n'+d.connections.map(c=>`  ${c.from} <-> ${c.to} (${c.shared.join(', ')})`).join('\\n');
    }
    if(d.type==='help'&&d.commands){
      resp+='\\n\\n'+d.commands.map(c=>`  ${c.cmd} - ${c.desc}`).join('\\n');
    }
    if(d.type==='list_items'&&d.items){
      resp+='\\n\\n'+d.items.map(i=>`  - ${i.title} [${i.type}]`).join('\\n');
    }
    chatHist.push({role:'bot',text:resp});
    await loadItems();
  }catch(e){
    chatHist.push({role:'bot',text:'Error: '+e.message});
  }
  renderChat($('ct'));
}

function quickChat(msg){$('ci').value=msg;sendChat();}

async function doReg(){
  try{
    const d=await api('/auth/register','POST',{username:v('r-u'),email:v('r-e'),password:v('r-p')});
    showMsg('amsg',d.message);tab='login';setTimeout(render,800);
  }catch(e){showMsg('amsg',e.message,true);}
}

async function doLogin(){
  try{
    const d=await api('/auth/login','POST',{username:v('l-u'),password:v('l-p')});
    T=d.access_token;U={id:d.user_id,username:d.username};localStorage.setItem('tk',T);
    await loadItems();tab='chat';render();
  }catch(e){showMsg('amsg',e.message,true);}
}

function logout(){T=null;U=null;items=[];chatHist=[];localStorage.removeItem('tk');tab='chat';render();}

function showMsg(id,text,err=false){const e=$(id);if(!e)return;e.className='msg '+(err?'err':'ok');e.textContent=text;}

async function loadItems(){try{const d=await api('/items');items=d.items||[];}catch(e){items=[];}}

async function deleteItem(id){
  try{
    items=items.filter(i=>i.id!==id);
    chatHist.push({role:'bot',text:'Item deleted'});
    renderTab();
  }catch(e){}
}

(async()=>{if(T){try{await loadItems();U=await api('/auth/me');}catch(e){T=null;localStorage.removeItem('tk');}}render();})();
</script>
</body>
</html>"""