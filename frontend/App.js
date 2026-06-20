import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [items, setItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      fetchItems();
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        username,
        password
      });
      const { access_token, user_id, username: userName } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser({ id: user_id, username: userName });
      setIsAuthenticated(true);
      setError('');
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/auth/register`, {
        username,
        email,
        password
      });
      await login(username, password);
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setActiveTab('dashboard');
  };

  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agent-status`);
      // For demo, we'll use mock data
      setItems([
        { id: 1, content: 'Project Ideas', source: 'manual', category: 'ideas' },
        { id: 2, content: 'Meeting Notes', source: 'google_keep', category: 'work' },
        { id: 3, content: 'Research Notes', source: 'browser', category: 'learning' },
      ]);
    } catch (err) {
      console.error('Failed to fetch items:', err);
    }
  };

  const addItem = async (content, sourceType = 'manual') => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/items`, {
        content,
        source_type: sourceType
      });
      setItems([...items, response.data.knowledge_item]);
      setError('');
    } catch (err) {
      setError('Failed to add item. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const searchKnowledge = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/search`, {
        query: searchQuery,
        max_results: 10
      });
      setSearchResults(response.data.results);
      setError('');
    } catch (err) {
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const syncSources = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/sync`);
      alert(`Sync completed! Found ${response.data.total_items} items.`);
    } catch (err) {
      setError('Sync failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="App">
        <AuthForm onLogin={login} onRegister={register} loading={loading} error={error} />
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Personal Knowledge Assistant</h1>
        <div className="user-info">
          <span>Welcome, {user?.username}</span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'add' ? 'active' : ''}
          onClick={() => setActiveTab('add')}
        >
          Add Item
        </button>
        <button 
          className={activeTab === 'search' ? 'active' : ''}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
        <button 
          className={activeTab === 'sources' ? 'active' : ''}
          onClick={() => setActiveTab('sources')}
        >
          Sources
        </button>
      </nav>

      <main className="main-content">
        {error && <div className="error-message">{error}</div>}
        
        {activeTab === 'dashboard' && (
          <Dashboard items={items} onSync={syncSources} loading={loading} />
        )}
        
        {activeTab === 'add' && (
          <AddItemForm onAdd={addItem} loading={loading} />
        )}
        
        {activeTab === 'search' && (
          <SearchPanel 
            query={searchQuery}
            setQuery={setSearchQuery}
            results={searchResults}
            onSearch={searchKnowledge}
            loading={loading}
          />
        )}
        
        {activeTab === 'sources' && (
          <SourcesPanel onSync={syncSources} loading={loading} />
        )}
      </main>
    </div>
  );
}

function AuthForm({ onLogin, onRegister, loading, error }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) {
      onLogin(username, password);
    } else {
      onRegister(username, email, password);
    }
  };

  return (
    <div className="auth-form">
      <h2>{isLogin ? 'Login' : 'Register'}</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        {!isLogin && (
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        )}
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
        </button>
      </form>
      <button 
        className="toggle-auth"
        onClick={() => setIsLogin(!isLogin)}
      >
        {isLogin ? 'Need an account? Register' : 'Already have an account? Login'}
      </button>
    </div>
  );
}

function Dashboard({ items, onSync, loading }) {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="dashboard-actions">
        <button onClick={onSync} disabled={loading}>
          {loading ? 'Syncing...' : 'Sync Sources'}
        </button>
      </div>
      <div className="items-list">
        <h3>Recent Items ({items.length})</h3>
        {items.length === 0 ? (
          <p>No items yet. Add some content to get started!</p>
        ) : (
          <ul>
            {items.map(item => (
              <li key={item.id} className="item-card">
                <div className="item-content">{item.content}</div>
                <div className="item-meta">
                  <span className="item-source">{item.source}</span>
                  <span className="item-category">{item.category}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function AddItemForm({ onAdd, loading }) {
  const [content, setContent] = useState('');
  const [sourceType, setSourceType] = useState('manual');

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd(content, sourceType);
    setContent('');
  };

  return (
    <div className="add-item-form">
      <h2>Add New Item</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your note, idea, or information..."
            rows={5}
            required
          />
        </div>
        <div className="form-group">
          <label>Source Type</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
          >
            <option value="manual">Manual Entry</option>
            <option value="google_keep">Google Keep</option>
            <option value="google_drive">Google Drive</option>
            <option value="browser">Browser</option>
          </select>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Item'}
        </button>
      </form>
    </div>
  );
}

function SearchPanel({ query, setQuery, results, onSearch, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <div className="search-panel">
      <h2>Search Knowledge Base</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for notes, ideas, information..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      
      {results.length > 0 && (
        <div className="search-results">
          <h3>Results ({results.length})</h3>
          <ul>
            {results.map((result, index) => (
              <li key={index} className="result-item">
                <div className="result-content">{result.content}</div>
                <div className="result-meta">
                  <span>Score: {result.score}</span>
                  <span>Type: {result.match_type}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function SourcesPanel({ onSync, loading }) {
  const [sources, setSources] = useState([]);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/sources`);
        setSources(response.data.sources);
      } catch (err) {
        console.error('Failed to fetch sources:', err);
      }
    };
    fetchSources();
  }, []);

  return (
    <div className="sources-panel">
      <h2>Connected Sources</h2>
      <div className="sources-actions">
        <button onClick={onSync} disabled={loading}>
          {loading ? 'Syncing...' : 'Sync All Sources'}
        </button>
      </div>
      <div className="sources-list">
        {sources.length === 0 ? (
          <p>No sources connected yet.</p>
        ) : (
          <ul>
            {sources.map((source, index) => (
              <li key={index} className="source-item">
                <span className="source-name">{source}</span>
                <span className="source-status">Connected</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;