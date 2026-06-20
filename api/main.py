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

    if any(w in msg for w in ["add note", "new note", "create note", "save note"]):
        title = message
        for w in ["add note", "new note", "create note", "save note", "about"]:
            title = title.replace(w, "")
        title = title.strip() or "Untitled Note"
        item = {"id": f"n{len(knowledge_base)+1}", "type": "note", "title": title.title(), "content": title, "tags": ["note"], "created_at": datetime.now().isoformat()}
        knowledge_base.append(item)
        return {"type": "note_added", "message": "Note added: " + title.title(), "item": item}

    if any(w in msg for w in ["add bookmark", "save bookmark", "bookmark"]):
        url_match = re.search(r'(https?://\S+)', message)
        url = url_match.group(1) if url_match else "https://example.com"
        title = message
        for w in ["add bookmark", "save bookmark", "bookmark"]:
            title = title.replace(w, "")
        title = title.replace(url, "").strip() or "My Bookmark"
        item = {"id": f"b{len(knowledge_base)+1}", "type": "bookmark", "title": title.title(), "url": url, "content": url, "tags": ["bookmark"], "created_at": datetime.now().isoformat()}
        knowledge_base.append(item)
        return {"type": "bookmark_added", "message": "Bookmark saved: " + title.title(), "item": item}

    if any(w in msg for w in ["search", "find", "look for"]):
        query = message
        for w in ["search for ", "search ", "find ", "look for "]:
            query = query.replace(w, "")
        query = query.strip() or message
        results = []
        for item in knowledge_base:
            searchable = f"{item.get('title','')} {item.get('content','')} {item.get('url','')} {' '.join(item.get('tags',[]))}".lower()
            score = 0
            if query.lower() in searchable:
                score = searchable.count(query.lower())
            else:
                for word in query.lower().split():
                    if len(word) > 2 and word in searchable:
                        score += 1
            if score > 0:
                results.append({**item, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        if results:
            return {"type": "search_results", "message": f"Found {len(results)} results for '{query}'", "results": results}
        return {"type": "no_results", "message": f"No results found for '{query}'."}

    if any(w in msg for w in ["summarize", "summary", "overview"]):
        if not knowledge_base:
            return {"type": "empty", "message": "No items to summarize yet."}
        notes = [i for i in knowledge_base if i["type"] == "note"]
        bookmarks = [i for i in knowledge_base if i["type"] == "bookmark"]
        all_tags = set()
        for item in knowledge_base:
            all_tags.update(item.get("tags", []))
        return {"type": "summary", "message": "Knowledge Base Summary", "stats": {"total": len(knowledge_base), "notes": len(notes), "bookmarks": len(bookmarks), "tags": list(all_tags)[:10]}}

    if any(w in msg for w in ["connect", "connection", "related"]):
        connections = []
        for i in range(len(knowledge_base)):
            for j in range(i+1, len(knowledge_base)):
                common = set(knowledge_base[i].get("tags",[])).intersection(set(knowledge_base[j].get("tags",[])))
                if common:
                    connections.append({"from": knowledge_base[i]["title"], "to": knowledge_base[j]["title"], "shared": list(common)})
        if connections:
            return {"type": "connections", "message": f"Found {len(connections)} connections", "connections": connections}
        return {"type": "no_connections", "message": "No connections found yet."}

    if any(w in msg for w in ["list", "show all", "show me", "what do i have"]):
        if not knowledge_base:
            return {"type": "empty", "message": "Your knowledge base is empty."}
        return {"type": "list_items", "message": f"You have {len(knowledge_base)} items", "items": knowledge_base[-10:]}

    if any(w in msg for w in ["delete", "remove"]):
        title_match = re.search(r'(?:delete|remove)\s+(.+)', message, re.I)
        if title_match:
            title = title_match.group(1).strip()
            for i, item in enumerate(knowledge_base):
                if title.lower() in item.get("title","").lower():
                    removed = knowledge_base.pop(i)
                    return {"type": "deleted", "message": f"Deleted: {removed['title']}"}
            return {"type": "not_found", "message": f"Could not find '{title}'."}
        return {"type": "clarify", "message": "What would you like to delete?"}

    if any(w in msg for w in ["help", "what can you do", "commands"]):
        return {"type": "help", "message": "Here is what I can do:", "commands": [
            {"cmd": "Add note about [topic]", "desc": "Create a note"},
            {"cmd": "Add bookmark [url]", "desc": "Save a bookmark"},
            {"cmd": "Search [query]", "desc": "Find items"},
            {"cmd": "Summarize", "desc": "Get overview"},
            {"cmd": "List", "desc": "Show all items"},
            {"cmd": "Find connections", "desc": "Related items"},
            {"cmd": "Delete [title]", "desc": "Remove item"},
        ]}

    return {"type": "chat", "message": "Try: 'Add note about meeting', 'Search for project', 'Summarize', 'Help'"}


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/auth/register")
async def register(body: UserRegister):
    user = auth_service.create_user(body.username, body.email, body.password)
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
    return result


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Knowledge Assistant - Multi-Agent System with Google ADK</title>

<!-- OpenGraph Meta Tags -->
<meta property="og:title" content="AI Knowledge Assistant - Multi-Agent System with Google ADK">
<meta property="og:description" content="Organize, search, and synthesize your knowledge with AI. Built with Google ADK, multi-agent systems, MCP servers, and security features.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://knowledge-assistant-rho.vercel.app">
<meta property="og:image" content="https://raw.githubusercontent.com/PremJibon/kaggle_submit/main/thumbnail.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AI Knowledge Assistant Dashboard">
<meta property="og:site_name" content="AI Knowledge Assistant">
<meta property="og:locale" content="en_US">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="AI Knowledge Assistant - Multi-Agent System with Google ADK">
<meta name="twitter:description" content="Organize, search, and synthesize your knowledge with AI. Built with Google ADK, multi-agent systems, MCP servers, and security features.">
<meta name="twitter:image" content="https://raw.githubusercontent.com/PremJibon/kaggle_submit/main/thumbnail.png">
<meta name="twitter:image:alt" content="AI Knowledge Assistant Dashboard">

<!-- Additional Meta -->
<meta name="description" content="AI Personal Knowledge Assistant - A multi-agent system for organizing, retrieving, and synthesizing information. Built with Google ADK, FastAPI, and deployed on Vercel.">
<meta name="keywords" content="AI, Knowledge Assistant, Multi-Agent System, Google ADK, MCP, FastAPI, Vercel, Kaggle Capstone">
<meta name="author" content="PremJibon">
<meta name="theme-color" content="#0B0D14">
<link rel="canonical" href="https://knowledge-assistant-rho.vercel.app">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#fafafa;min-height:100vh}
.app{max-width:800px;margin:0 auto;padding:16px}
h1{font-size:2rem;text-align:center;margin:20px 0 4px;background:linear-gradient(135deg,#89AACC,#4E85BF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{text-align:center;color:#737373;margin-bottom:20px;font-size:.9rem}
.tabs{display:flex;gap:6px;justify-content:center;margin-bottom:16px;flex-wrap:wrap}
.tabs button{padding:8px 16px;border:1px solid #262626;background:transparent;color:#737373;border-radius:999px;cursor:pointer;font-size:.85rem}
.tabs button.on{background:#fafafa;color:#0a0a0a;border-color:#fafafa}
.tabs button:hover{color:#fafafa;border-color:#737373}
.card{background:#141414;border:1px solid #262626;border-radius:12px;padding:20px;margin-bottom:16px}
.card h2{font-size:1.1rem;margin-bottom:14px}
.inp{display:flex;gap:8px;margin-bottom:12px}
.inp input,.inp textarea,.inp select{flex:1;padding:12px;border:1px solid #262626;border-radius:8px;background:#0a0a0a;color:#fafafa;font-size:.9rem;outline:none}
.inp input:focus,.inp textarea:focus{border-color:#3b82f6}
.inp textarea{min-height:80px;resize:vertical}
.btn{padding:10px 20px;border:none;border-radius:8px;font-size:.9rem;font-weight:600;cursor:pointer}
.bp{background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff}
.bp:hover{opacity:.9}
.bs{background:#1a1a1a;color:#fafafa;border:1px solid #262626}
.bsm{background:#ef4444;color:#fff;font-size:.75rem;padding:4px 10px}
.msg{background:#0a0a0a;border:1px solid #262626;border-radius:8px;padding:12px;margin-top:12px;font-size:.85rem;white-space:pre-wrap;max-height:200px;overflow-y:auto}
.msg.ok{border-left:3px solid #10b981}
.msg.err{border-left:3px solid #ef4444;color:#ef4444}
.hidden{display:none}
.item{background:#0a0a0a;border:1px solid #262626;border-radius:8px;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}
.item:hover{border-color:#3b82f6}
.item .info{flex:1}
.item .t{font-weight:600;font-size:.9rem}
.item .c{color:#737373;font-size:.8rem;margin-top:2px}
.tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:.7rem;background:rgba(59,130,246,.12);color:#3b82f6;margin-right:4px}
.tag.g{background:rgba(16,185,129,.12);color:#10b981}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px}
.stat{background:#141414;border:1px solid #262626;border-radius:8px;padding:12px;text-align:center}
.stat .n{font-size:1.5rem;font-weight:700;color:#3b82f6}
.stat .l{color:#737373;font-size:.7rem;margin-top:2px}
.cmds{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px}
.cmd{background:#0a0a0a;border:1px solid #262626;border-radius:8px;padding:10px;cursor:pointer}
.cmd:hover{border-color:#3b82f6}
.cmd .c{font-size:.85rem;font-weight:500}
.cmd .d{font-size:.75rem;color:#737373}
.ch{max-height:400px;overflow-y:auto;margin-bottom:12px}
.ch::-webkit-scrollbar{width:4px}
.ch::-webkit-scrollbar-thumb{background:#262626;border-radius:4px}
.cm{margin-bottom:8px}
.cm.u{text-align:right}
.cm .b{display:inline-block;max-width:80%;padding:10px 14px;border-radius:12px;font-size:.85rem;line-height:1.5;text-align:left}
.cm.u .b{background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff}
.cm.b .b{background:#1a1a1a;border:1px solid #262626}
.guide{display:flex;gap:12px;padding:10px;background:#0a0a0a;border:1px solid #262626;border-radius:8px;margin-bottom:8px}
.guide .n{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#89AACC,#4E85BF);color:#fff;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;flex-shrink:0}
.guide .tx h4{font-size:.85rem;margin-bottom:2px}
.guide .tx p{color:#737373;font-size:.8rem}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.cm{animation:fadeIn .2s}
@media(max-width:600px){.stats{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="app" id="app"></div>
<script>
var T=localStorage.getItem('tk'),U=null,items=[],tab='chat',ch=[];
function $(i){return document.getElementById(i)}
function v(i){var e=$(i);return e?e.value.trim():''}
function api(u,m,b){var h={'Content-Type':'application/json'};if(T)h['Authorization']='Bearer '+T;var o={method:m||'GET',headers:h};if(b)o.body=JSON.stringify(b);return fetch(u,o).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Error')});return r.json()})}
function render(){if(!T){renderAuth();return}renderApp()}
function renderAuth(){var isReg=tab==='reg';$('app').innerHTML='<header><h1>AI Knowledge Assistant</h1><p class="sub">Organize, search and synthesize your knowledge</p></header><div class="card"><div class="tabs"><button class="'+(isReg?'on':'')+'" onclick=\\"tab=\\'reg\\';render()\\">Register</button><button class="'+(!isReg?'on':'')+'" onclick=\\"tab=\\'login\\';render()\\">Login</button></div>'+(isReg?'<div class="inp"><input id="r-u" placeholder="Username"></div><div class="inp"><input id="r-e" type="email" placeholder="Email"></div><div class="inp"><input id="r-p" type="password" placeholder="Password"></div><button class="btn bp" onclick="doReg()" style="width:100%">Create Account</button>':'<div class="inp"><input id="l-u" placeholder="Username"></div><div class="inp"><input id="l-p" type="password" placeholder="Password"></div><button class="btn bp" onclick="doLogin()" style="width:100%">Sign In</button>')+'<div id="am" class="msg hidden"></div></div><div class="card"><h2>Getting Started</h2><div class="guide"><div class="n">1</div><div class="tx"><h4>Create Account</h4><p>Register with any username, email, and password</p></div></div><div class="guide"><div class="n">2</div><div class="tx"><h4>Chat Commands</h4><p>Type natural commands like "add note about meeting" or "search for project"</p></div></div><div class="guide"><div class="n">3</div><div class="tx"><h4>Browse and Search</h4><p>Use the Browse tab to see all items and filter by tags</p></div></div></div>'}
function renderApp(){$('app').innerHTML='<header><div style="display:flex;justify-content:space-between;align-items:center"><div><h1>Knowledge Assistant</h1><p class="sub">Welcome, <span style="color:#10b981">'+(U?U.username:'User')+'</span></p></div><button class="btn bs" onclick="logout()" style="font-size:.75rem;padding:6px 12px">Logout</button></div></header><div class="stats"><div class="stat"><div class="n">'+items.length+'</div><div class="l">Total</div></div><div class="stat"><div class="n">'+items.filter(function(i){return i.type==='note'}).length+'</div><div class="l">Notes</div></div><div class="stat"><div class="n">'+items.filter(function(i){return i.type==='bookmark'}).length+'</div><div class="l">Bookmarks</div></div><div class="stat"><div class="n">'+new Set(items.flatMap(function(i){return i.tags||[]})).size+'</div><div class="l">Tags</div></div></div><div class="tabs"><button class="'+(tab==='chat'?'on':'')+'" onclick="tab=\\'chat\\';render()">Chat</button><button class="'+(tab==='browse'?'on':'')+'" onclick="tab=\\'browse\\';render()">Browse</button><button class="'+(tab==='guide'?'on':'')+'" onclick="tab=\\'guide\\';render()">Guide</button></div><div id="ct"></div>';renderTab()}
function renderTab(){var c=$('ct');if(!c)return;if(tab==='chat')renderChat(c);else if(tab==='browse')renderBrowse(c);else if(tab==='guide')renderGuide(c)}
function renderChat(c){var h='';for(var i=0;i<ch.length;i++){h+='<div class="cm '+(ch[i].role==='user'?'u':'b')+'"><div class="b">'+ch[i].text.replace(/\\n/g,'<br>')+'</div></div>'}c.innerHTML='<div class="card"><h2>Chat with Assistant</h2><div class="ch" id="ch">'+h+'</div><div class="inp" style="position:relative"><textarea id="ci" placeholder="Type: add note, search, summarize, help..." rows="1" onkeydown="if(event.key===\\'Enter\\'&&!event.shiftKey){event.preventDefault();sendChat()}"></textarea><button class="btn bp" onclick="sendChat()" style="position:absolute;right:8px;bottom:8px">Send</button></div></div><div class="card"><h2>Quick Commands</h2><div class="cmds"><div class="cmd" onclick="qc(\\'Add note about my meeting\\')"><div class="c">Add note</div><div class="d">Create a note</div></div><div class="cmd" onclick="qc(\\'Add bookmark https://google.com Google\\')"><div class="c">Add bookmark</div><div class="d">Save a URL</div></div><div class="cmd" onclick="qc(\\'Search for note\\')"><div class="c">Search</div><div class="d">Find items</div></div><div class="cmd" onclick="qc(\\'Summarize\\')"><div class="c">Summarize</div><div class="d">Overview</div></div><div class="cmd" onclick="qc(\\'List all items\\')"><div class="c">List</div><div class="d">Show all</div></div><div class="cmd" onclick="qc(\\'Find connections\\')"><div class="c">Connections</div><div class="d">Related</div></div><div class="cmd" onclick="qc(\\'Help\\')"><div class="c">Help</div><div class="d">Commands</div></div></div></div>';var el=$('ch');if(el)el.scrollTop=el.scrollHeight}
function renderBrowse(c){var tags=[];items.forEach(function(i){(i.tags||[]).forEach(function(t){if(tags.indexOf(t)===-1)tags.push(t)})});var opts='<option value="">All Tags</option>';tags.forEach(function(t){opts+='<option value="'+t+'">'+t+'</option>'});c.innerHTML='<div class="card"><h2>Browse Items</h2><div class="inp"><select id="ft" onchange="filterItems()" style="flex:1;padding:10px;border:1px solid #262626;border-radius:8px;background:#0a0a0a;color:#fafafa">'+opts+'</select></div><div id="il"></div></div>';filterItems()}
function filterItems(){var tag=v('ft');var f=tag?items.filter(function(i){return(i.tags||[]).indexOf(tag)!==-1}):items;var el=$('il');if(!el)return;if(f.length===0){el.innerHTML='<p style="color:#737373;text-align:center;padding:20px">No items yet</p>';return}var h='';f.forEach(function(i){h+='<div class="item"><div class="info"><div class="t">'+(i.title||'Untitled')+'</div><div class="c">'+(i.content||i.url||'').substring(0,100)+'</div><div>'+(i.tags||[]).map(function(t){return '<span class="tag">'+t+'</span>'}).join('')+'<span class="tag g">'+i.type+'</span></div></div><button class="btn bsm" onclick="del(\\''+i.id+'\\')">X</button></div>'});el.innerHTML=h}
function renderGuide(c){c.innerHTML='<div class="card"><h2>How to Use</h2><div class="guide"><div class="n">1</div><div class="tx"><h4>Add Notes</h4><p>Type "add note about [topic]" in the chat to save ideas.</p></div></div><div class="guide"><div class="n">2</div><div class="tx"><h4>Save Bookmarks</h4><p>Type "add bookmark [url] [title]" to save links.</p></div></div><div class="guide"><div class="n">3</div><div class="tx"><h4>Search</h4><p>Type "search for [keyword]" to find items.</p></div></div><div class="guide"><div class="n">4</div><div class="tx"><h4>Summarize</h4><p>Type "summarize" to get an overview.</p></div></div><div class="guide"><div class="n">5</div><div class="tx"><h4>List</h4><p>Type "list" to see all items.</p></div></div><div class="guide"><div class="n">6</div><div class="tx"><h4>Help</h4><p>Type "help" to see all commands.</p></div></div></div><div class="card"><h2>Commands</h2><div class="cmds"><div class="cmd" onclick="qc(\\'Add note about my meeting\\')"><div class="c">Add note about [topic]</div><div class="d">Create note</div></div><div class="cmd" onclick="qc(\\'Add bookmark https://example.com Example\\')"><div class="c">Add bookmark [url]</div><div class="d">Save bookmark</div></div><div class="cmd" onclick="qc(\\'Search for meeting\\')"><div class="c">Search [query]</div><div class="d">Find items</div></div><div class="cmd" onclick="qc(\\'Summarize\\')"><div class="c">Summarize</div><div class="d">Get overview</div></div><div class="cmd" onclick="qc(\\'List all items\\')"><div class="c">List</div><div class="d">Show all</div></div><div class="cmd" onclick="qc(\\'Find connections\\')"><div class="c">Connections</div><div class="d">Related items</div></div><div class="cmd" onclick="qc(\\'Delete [title]\\')"><div class="c">Delete [title]</div><div class="d">Remove item</div></div></div></div>'}
function sendChat(){var ci=$('ci');if(!ci)return;var msg=ci.value.trim();if(!msg)return;ci.value='';ch.push({role:'user',text:msg});renderChat($('ct'));api('/chat','POST',{message:msg}).then(function(d){var resp=d.message;if(d.type==='search_results'&&d.results){resp+='\\n\\n'+d.results.map(function(r){return '  - '+r.title+' ('+r.type+')'}).join('\\n')}if(d.type==='summary'&&d.stats){resp+='\\n\\nNotes: '+d.stats.notes+' | Bookmarks: '+d.stats.bookmarks}if(d.type==='connections'&&d.connections){resp+='\\n\\n'+d.connections.map(function(c){return '  '+c.from+' <-> '+c.to+' ('+c.shared.join(', ')+')'}).join('\\n')}if(d.type==='help'&&d.commands){resp+='\\n\\n'+d.commands.map(function(c){return '  '+c.cmd+' - '+c.desc}).join('\\n')}if(d.type==='list_items'&&d.items){resp+='\\n\\n'+d.items.map(function(i){return '  - '+i.title+' ['+i.type+']'}).join('\\n')}ch.push({role:'bot',text:resp});loadItems().then(function(){renderChat($('ct'))})}).catch(function(e){ch.push({role:'bot',text:'Error: '+e.message});renderChat($('ct'))})}
function qc(msg){$('ci').value=msg;sendChat()}
function doReg(){api('/auth/register','POST',{username:v('r-u'),email:v('r-e'),password:v('r-p')}).then(function(d){showMsg('am',d.message);tab='login';setTimeout(render,800)}).catch(function(e){showMsg('am',e.message,true)})}
function doLogin(){api('/auth/login','POST',{username:v('l-u'),password:v('l-p')}).then(function(d){T=d.access_token;U={id:d.user_id,username:d.username};localStorage.setItem('tk',T);loadItems().then(function(){tab='chat';render()})}).catch(function(e){showMsg('am',e.message,true)})}
function logout(){T=null;U=null;items=[];ch=[];localStorage.removeItem('tk');tab='chat';render()}
function showMsg(id,text,err){var e=$(id);if(!e)return;e.className='msg '+(err?'err':'ok');e.textContent=text}
function loadItems(){return api('/items').then(function(d){items=d.items||[]}).catch(function(){items=[]})}
function del(id){items=items.filter(function(i){return i.id!==id});ch.push({role:'bot',text:'Item deleted'});renderTab()}
(function(){if(T){loadItems().then(function(){return api('/auth/me')}).then(function(u){U=u;tab='chat';render()}).catch(function(){T=null;localStorage.removeItem('tk');render()})}else{render()}})();
</script>
</body>
</html>"""