# AI Personal Knowledge Assistant

A multi-agent system that helps users organize, retrieve, and synthesize information from various sources. Built as a capstone project for the 5-Day AI Agents: Intensive Vibe Coding Course With Google.

## Key Features

### Multi-Agent System
- **Ingestion Agent**: Processes and normalizes incoming information
- **Retrieval Agent**: Finds relevant information using semantic search
- **Synthesis Agent**: Combines information and generates insights
- **Organization Agent**: Tags, categorizes, and creates knowledge graphs

### MCP Server Integration
- **Google Keep**: Sync notes from Google Keep
- **Google Drive**: Access documents and files
- **Browser**: Import bookmarks and history

### Security Features
- **User Authentication**: JWT-based authentication
- **Data Encryption**: AES-256 encryption for sensitive data
- **Audit Logging**: Track all user actions and data access
- **Privacy Controls**: User consent and data retention policies

## Architecture

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

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Web framework
- **Google ADK** - Agent development
- **PostgreSQL** - Database
- **Redis** - Caching

### Frontend
- **React 18**
- **Axios** - HTTP client
- **CSS3** - Styling

### Security
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **cryptography** - Data encryption

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knowledge-assistant
   ```

2. **Set up the backend**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings
   DATABASE_URL=postgresql://user:password@localhost/knowledge_assistant
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-secret-key
   GOOGLE_KEEP_API_KEY=your-google-keep-api-key
   GOOGLE_DRIVE_API_KEY=your-google-drive-api-key
   ```

5. **Run the application**
   ```bash
   # Terminal 1 - Backend
   cd api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login a user

### Knowledge Management
- `POST /items` - Create a new item
- `POST /search` - Search the knowledge base
- `POST /synthesize` - Synthesize information from multiple items

### Sources
- `GET /sources` - Get connected sources
- `GET /sync` - Sync content from all sources

### System
- `GET /health` - Health check
- `GET /agent-status` - Get agent status
- `GET /audit` - Get audit logs

## Project Structure

```
knowledge-assistant/
├── agents/                    # Agent implementations
│   ├── base_agent.py
│   ├── ingestion_agent.py
│   ├── retrieval_agent.py
│   ├── synthesis_agent.py
│   ├── organization_agent.py
│   └── coordinator.py
├── mcp_servers/               # MCP server connectors
│   ├── google_keep_connector.py
│   ├── gdrive_connector.py
│   ├── browser_connector.py
│   └── knowledge_mcp_server.py
├── security/                  # Security features
│   ├── auth.py
│   ├── encryption.py
│   └── audit.py
├── api/                       # FastAPI backend
│   └── main.py
├── frontend/                  # React frontend
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── package.json
├── tests/                     # Test files
├── docs/                      # Documentation
└── requirements.txt           # Python dependencies
```

## Testing

### Backend Tests
```bash
cd knowledge-assistant
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Security Considerations

1. **Data Encryption**: All sensitive data is encrypted at rest using AES-256
2. **Authentication**: JWT tokens with secure expiration
3. **Input Validation**: All user inputs are validated and sanitized
4. **Audit Logging**: All actions are logged for security monitoring
5. **API Rate Limiting**: Prevents abuse and ensures fair usage

## Demo Scenarios

1. **Add a Note**: Create a new note via the web interface
2. **Search Knowledge**: Query for related information
3. **Agent Collaboration**: Show how agents work together
4. **MCP Integration**: Demonstrate syncing from external sources
5. **Security Features**: Show encryption and audit logging

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google ADK team for the agent development framework
- FastAPI team for the web framework
- React team for the frontend library
- 5-Day AI Agents course instructors and mentors