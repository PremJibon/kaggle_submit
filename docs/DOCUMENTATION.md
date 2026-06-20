# AI Personal Knowledge Assistant - Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agent System](#agent-system)
4. [MCP Server Integration](#mcp-server-integration)
5. [Security Features](#security-features)
6. [API Reference](#api-reference)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Overview

The AI Personal Knowledge Assistant is a multi-agent system that helps users organize, retrieve, and synthesize information from various sources. It demonstrates key concepts from the 5-Day AI Agents course:

- **Multi-agent systems** - Four coordinated agents working together
- **MCP servers** - Integration with external applications
- **Agent skills** - Specialized capabilities for each agent
- **Security features** - User data privacy and protection

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Knowledge Assistant                     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Ingestion   │  │ Retrieval   │  │ Synthesis   │     │
│  │ Agent       │  │ Agent       │  │ Agent       │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          │                               │
│                 ┌─────────────────┐                      │
│                 │  Organization   │                      │
│                 │  Agent          │                      │
│                 └─────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### Component Overview

1. **Agent System** - Four specialized agents that work together
2. **MCP Server** - Connects to external sources (Google Keep, Drive, Browser)
3. **Security Layer** - Authentication, encryption, and audit logging
4. **API Backend** - FastAPI-based REST API
5. **Web Frontend** - React-based user interface

## Agent System

### Agent Types

#### 1. Ingestion Agent
**Purpose**: Processes incoming information from various sources
**Skills**:
- Content parsing and normalization
- Metadata extraction (dates, tags, sources)
- Format conversion (HTML, Markdown, JSON)

**Example Usage**:
```python
from agents.ingestion_agent import IngestionAgent

agent = IngestionAgent()
await agent.initialize()

result = await agent.process({
    "content": "Meeting notes about the project deadline",
    "source_type": "manual",
    "format": "text"
})
```

#### 2. Retrieval Agent
**Purpose**: Finds and ranks relevant information
**Skills**:
- Semantic search using embeddings
- Keyword matching
- Result ranking and filtering

**Example Usage**:
```python
from agents.retrieval_agent import RetrievalAgent

agent = RetrievalAgent()
await agent.initialize()

# Add items to knowledge base
await agent.add_to_knowledge_base({
    "id": "item1",
    "content": "Project deadline is next Friday",
    "metadata": {"tags": ["deadline", "project"]}
})

# Search
result = await agent.process({
    "query": "deadline",
    "strategy": "combined",
    "max_results": 10
})
```

#### 3. Synthesis Agent
**Purpose**: Combines information and generates insights
**Skills**:
- Summary generation
- Information comparison
- Connection discovery

**Example Usage**:
```python
from agents.synthesis_agent import SynthesisAgent

agent = SynthesisAgent()
await agent.initialize()

items = [
    {"content": "Note 1 about AI", "metadata": {"tags": ["ai"]}},
    {"content": "Note 2 about ML", "metadata": {"tags": ["ml"]}}
]

result = await agent.process({
    "items": items,
    "type": "summary"
})
```

#### 4. Organization Agent
**Purpose**: Tags, categorizes, and organizes content
**Skills**:
- Automatic categorization
- Auto-tagging
- Knowledge graph creation

**Example Usage**:
```python
from agents.organization_agent import OrganizationAgent

agent = OrganizationAgent()
await agent.initialize()

# Categorize content
result = await agent.process({
    "content": "Meeting notes about project deadline",
    "metadata": {},
    "action": "categorize"
})

# Auto-tag
tag_result = await agent.process({
    "content": "Important meeting about the project",
    "metadata": {},
    "action": "tag"
})
```

### Agent Coordinator

The Agent Coordinator manages all agents and orchestrates their workflows:

```python
from agents.coordinator import AgentCoordinator

coordinator = AgentCoordinator()
await coordinator.initialize()

# Process an item through the full pipeline
result = await coordinator.process_item({
    "content": "Important meeting notes",
    "source_type": "manual"
})

# Search the knowledge base
search_result = await coordinator.search_knowledge("meeting")

# Synthesize information
synthesis_result = await coordinator.synthesize_information(
    items=[item1, item2],
    synthesis_type="summary"
)
```

## MCP Server Integration

### Available Connectors

#### 1. Google Keep Connector
**Features**:
- Fetch notes from Google Keep
- Create new notes
- Update existing notes
- Search notes

**Setup**:
```python
from mcp_servers.google_keep_connector import GoogleKeepConnector

connector = GoogleKeepConnector(api_key="your-api-key")
notes = await connector.fetch_notes()
```

#### 2. Google Drive Connector
**Features**:
- Fetch files from Google Drive
- Get file content
- Create new files
- Search files

**Setup**:
```python
from mcp_servers.gdrive_connector import GoogleDriveConnector

connector = GoogleDriveConnector(api_key="your-api-key")
files = await connector.fetch_files()
```

#### 3. Browser Connector
**Features**:
- Fetch bookmarks
- Fetch browsing history
- Add/remove bookmarks
- Search bookmarks

**Setup**:
```python
from mcp_servers.browser_connector import BrowserConnector

connector = BrowserConnector()
bookmarks = await connector.fetch_bookmarks()
```

### Knowledge MCP Server

The main MCP server coordinates all connectors:

```python
from mcp_servers.knowledge_mcp_server import KnowledgeMCPServer

server = KnowledgeMCPServer(
    google_keep_api_key="your-key",
    google_drive_api_key="your-key"
)

# Sync from all sources
sync_result = await server.sync_all()

# Search across all sources
search_result = await server.search_all("meeting")
```

## Security Features

### Authentication

JWT-based authentication system:

```python
from security.auth import AuthService

auth = AuthService()

# Create user
user = auth.create_user(
    username="john",
    email="john@example.com",
    password="securepassword"
)

# Login
user = auth.authenticate_user("john", "securepassword")

# Create token
token = auth.create_access_token({"sub": user.id})

# Verify token
payload = auth.verify_token(token)
```

### Data Encryption

AES-256 encryption for sensitive data:

```python
from security.encryption import EncryptionService

encryption = EncryptionService(password="user-password")

# Encrypt data
encrypted = encryption.encrypt_data("sensitive information")

# Decrypt data
decrypted = encryption.decrypt_data(encrypted)

# Encrypt dictionary
encrypted_dict = encryption.encrypt_dict({"key": "value"})
```

### Audit Logging

Track all user actions:

```python
from security.audit import AuditLogger

logger = AuditLogger()

# Log user action
logger.log_user_action(
    user_id="user123",
    action="create_item",
    resource="item",
    details={"item_id": "item456"}
)

# Get user activity
activity = logger.get_user_activity("user123")

# Export logs
logs = logger.export_events(format="json")
```

## API Reference

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john",
  "password": "securepassword"
}
```

### Knowledge Management Endpoints

#### Create Item
```http
POST /items
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Important meeting notes",
  "source_type": "manual",
  "format": "text"
}
```

#### Search Knowledge
```http
POST /search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "meeting",
  "max_results": 10
}
```

#### Synthesize Information
```http
POST /synthesize
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {"content": "Note 1", "metadata": {}},
    {"content": "Note 2", "metadata": {}}
  ],
  "synthesis_type": "summary"
}
```

### Source Management Endpoints

#### Get Sources
```http
GET /sources
Authorization: Bearer <token>
```

#### Sync Sources
```http
GET /sync
Authorization: Bearer <token>
```

### System Endpoints

#### Health Check
```http
GET /health
```

#### Agent Status
```http
GET /agent-status
Authorization: Bearer <token>
```

#### Audit Logs
```http
GET /audit?limit=100
Authorization: Bearer <token>
```

## Deployment

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Deployment

1. **Set up the backend**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up the frontend**:
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start the application**:
   ```bash
   python start.py
   ```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill the process
   taskkill /PID <process_id> /F
   ```

2. **Database connection issues**:
   - Ensure PostgreSQL is running
   - Check database credentials in .env
   - Verify database exists

3. **Redis connection issues**:
   - Ensure Redis is running
   - Check Redis URL in .env

4. **API key issues**:
   - Verify API keys are correct
   - Check API key permissions
   - Ensure API keys are not expired

### Logs

Check application logs:
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs db
```

### Performance Issues

1. **Slow search**:
   - Reduce the number of items in knowledge base
   - Use simpler search strategies
   - Increase Redis cache TTL

2. **Memory issues**:
   - Monitor memory usage
   - Implement pagination for large datasets
   - Use connection pooling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License.