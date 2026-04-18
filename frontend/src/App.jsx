import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Home, Library as LibraryIcon, MessageSquare, Database, Settings, BookOpen, Search, Send, Plus, Loader2, CheckCircle2, ShieldAlert, LogIn, Mail } from 'lucide-react';
import React, { useState, useEffect, useRef } from 'react';

const API_BASE = window.location.origin + '/api';

// --- Dashboard Component ---
function Dashboard() {
  const [health, setHealth] = useState('Checking...');
  const [books, setBooks] = useState([]);
  const [queryCount, setQueryCount] = useState(0);

  useEffect(() => {
    fetch(`${API_BASE}/health/`)
      .then(res => res.json())
      .then(data => {
        setHealth(data.status === 'healthy' ? 'Healthy' : 'Degraded');
        if (data.query_count !== undefined) setQueryCount(data.query_count);
      })
      .catch(() => setHealth('Offline'));

    fetch(`${API_BASE}/books/`)
      .then(res => res.json())
      .then(data => setBooks(data))
      .catch(console.error);
  }, []);

  const stats = [
    { label: "Books in Store", value: books.length.toString(), icon: <BookOpen className="text-primary w-6 h-6" /> },
    { label: "AI Insights Generated", value: queryCount.toString(), icon: <MessageSquare className="text-secondary w-6 h-6" /> },
    { label: "System Status", value: health, icon: <Database className={`${health === 'Healthy' ? 'text-green-500' : 'text-red-500'} w-6 h-6`} /> }
  ];

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <h1 className="text-4xl font-bold mb-2">Welcome to <span className="gradient-text">NSR BOOKS</span></h1>
      <p className="text-slate-500 mb-8 text-lg">Your smart online bookstore.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, i) => (
          <div key={i} className="glass p-6 rounded-2xl flex items-center justify-between hover:scale-[1.02] transition-transform cursor-pointer">
            <div>
              <p className="text-slate-500 text-sm font-medium">{stat.label}</p>
              <h3 className="text-3xl font-bold mt-1">{stat.value}</h3>
            </div>
            <div className="p-4 bg-slate-100 rounded-xl">
              {stat.icon}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-2xl">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><BookOpen className="w-5 h-5 text-primary"/> Recent Documents</h2>
          <div className="space-y-4">
            {books.length === 0 ? (
              <p className="text-slate-500 text-sm">No documents found. Use the scraper to add some.</p>
            ) : books.slice(0, 4).map((book, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors cursor-pointer border border-transparent hover:border-slate-300">
                <div className="flex items-center gap-4">
                  {book.image_url ? (
                    <img src={book.image_url} alt={book.title} className="w-10 h-10 rounded-lg object-cover shadow-lg" />
                  ) : (
                    <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center font-bold text-white shadow-lg">
                      {book.title.charAt(0)}
                    </div>
                  )}
                  <div>
                    <h4 className="font-semibold truncate w-48 text-sm">{book.title}</h4>
                    <p className="text-xs text-slate-500">₹{book.price} • {book.rating} Rating</p>
                  </div>
                </div>
                <span className="text-[10px] uppercase tracking-wider bg-primary/20 text-primary px-3 py-1 rounded-full font-bold">Analyzed</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center">
          <ShieldAlert className="w-16 h-16 text-slate-500/30 mb-4" />
          <h2 className="text-xl font-bold mb-2">App Status</h2>
          <p className="text-slate-500 text-sm max-w-sm mb-6">Database connection is active. The smart search engine is ready to help you find books.</p>
          <Link to="/scraper" className="text-primary hover:text-slate-900 transition-colors font-semibold text-sm underline underline-offset-4">Configure Scraper Settings</Link>
        </div>
      </div>
    </div>
  );
}

// --- Scraper Component ---
function Scraper() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const runScraper = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${API_BASE}/scrape/`, { method: 'POST' });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ status: 'error', message: 'Failed to connect to backend.' });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="glass p-10 rounded-[2rem] text-center border-slate-200 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2"></div>
        
        <Database className="w-20 h-20 text-primary mx-auto mb-6 drop-shadow-[0_0_15px_rgba(79,70,229,0.5)]" />
        <h2 className="text-4xl font-bold mb-4">Book Finder Engine</h2>
        <p className="text-slate-500 mb-10 leading-relaxed max-w-xl mx-auto text-lg">Run the automated crawler to fetch new documents, extract their text content, and embed them into the Vector Database (ChromaDB).</p>
        
        <button 
          onClick={runScraper}
          disabled={loading}
          className="bg-gradient-to-r from-primary to-secondary text-white px-10 py-5 rounded-2xl font-bold text-lg hover:scale-105 transition-all flex items-center gap-4 mx-auto disabled:opacity-50 disabled:hover:scale-100 shadow-[0_10px_40px_-10px_rgba(236,72,153,0.5)]"
        >
          {loading ? <Loader2 className="animate-spin w-6 h-6" /> : <Database className="w-6 h-6" />}
          {loading ? 'Looking for books...' : 'Add New Books'}
        </button>

        {result && (
          <div className={`mt-10 p-6 rounded-2xl text-left flex items-start gap-4 transition-all duration-500 ${result.status === 'success' ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
            <CheckCircle2 className={`w-8 h-8 shrink-0 ${result.status === 'success' ? 'text-green-500' : 'text-red-500'}`} />
            <div>
              <h4 className="font-bold text-xl mb-1">{result.status === 'success' ? 'Pipeline Complete!' : 'Error'}</h4>
              <p className="text-slate-500 text-sm">{result.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// --- RAG Chat Component ---
function Chat() {
  const [messages, setMessages] = useState([{ role: 'ai', content: 'Hello! I am NSR AI. I know everything about the books in our shop. How can I help you today?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const sendQuery = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/query/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg })
      });
      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: data.response,
        sources: data.sources 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'System error: Could not contact the vector database.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto glass rounded-3xl overflow-hidden border-slate-200 shadow-2xl animate-in fade-in zoom-in-95 duration-500">
      <div className="p-6 border-b border-slate-200 bg-surface/50 backdrop-blur-md flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2"><MessageSquare className="text-primary w-5 h-5"/> NSR Smart Assistant</h2>
          <p className="text-xs text-slate-500 mt-1 tracking-wide uppercase">AI-Powered Search</p>
        </div>
        <div className="flex items-center gap-2 bg-green-500/10 px-3 py-1.5 rounded-full border border-green-500/20">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs text-green-500 font-bold tracking-wider">ONLINE</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
            <div className={`max-w-[80%] rounded-2xl p-5 shadow-lg ${msg.role === 'user' ? 'bg-gradient-to-br from-primary to-secondary text-slate-900 rounded-br-none' : 'bg-surface border border-slate-200 rounded-bl-none'}`}>
              <p className="leading-relaxed text-sm md:text-base">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-300">
                  <p className="text-[10px] font-bold tracking-widest mb-3 opacity-60 uppercase flex items-center gap-2">
                    <Database className="w-3 h-3" /> References:
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {msg.sources.map((s, idx) => <span key={idx} className="text-xs bg-black/30 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-500 font-medium">{s}</span>)}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl p-5 bg-surface border border-slate-200 rounded-bl-none flex gap-3 items-center">
              <span className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce"></span>
              <span className="w-2.5 h-2.5 bg-secondary rounded-full animate-bounce delay-100"></span>
              <span className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce delay-200"></span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={sendQuery} className="p-4 border-t border-slate-200 bg-surface/80 backdrop-blur-md">
        <div className="flex gap-3 relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..." 
            className="flex-1 bg-background border border-slate-300 rounded-2xl px-6 py-4 outline-none focus:border-primary/50 transition-colors text-slate-900 placeholder:text-slate-500 shadow-inner"
          />
          <button type="submit" disabled={loading || !input.trim()} className="bg-gradient-to-r from-primary to-secondary text-white px-8 py-4 rounded-2xl transition-all disabled:opacity-50 hover:scale-[1.02] active:scale-95 flex items-center gap-2 shadow-[0_5px_20px_-5px_rgba(79,70,229,0.5)]">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}

// --- Library Component ---
function Library() {
  const [books, setBooks] = useState([]);
  
  useEffect(() => {
    fetch(`${API_BASE}/books/`)
      .then(res => res.json())
      .then(data => setBooks(data))
      .catch(console.error);
  }, []);

  const buyBook = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE}/books/${id}/buy/`, { method: 'POST' });
      const data = await res.json();
      setBooks(prev => prev.map(b => b.id === id ? { ...b, purchases_count: data.purchases_count } : b));
      alert('Purchase successful!');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto h-full flex flex-col animate-in fade-in duration-500">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold">Document Library</h2>
          <p className="text-slate-500 mt-1 text-lg">Browse our books and check out our bestsellers.</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 bg-surface/50 px-5 py-3 rounded-2xl border border-slate-200 focus-within:border-primary/50 transition-colors shadow-inner">
            <Search className="w-5 h-5 text-slate-500" />
            <input type="text" placeholder="Search library..." className="bg-transparent border-none outline-none text-slate-900 w-48 placeholder:text-slate-500/50" />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto pb-8">
        {books.length === 0 ? (
          <div className="h-[60vh] flex flex-col items-center justify-center glass rounded-[2rem] border-slate-200 border-dashed">
            <BookOpen className="w-16 h-16 text-slate-300 mb-6" />
            <p className="text-slate-500 text-xl font-medium">Your library is currently empty.</p>
            <p className="text-sm text-slate-500/60 mt-2">Click 'Update Books' to bring in new titles.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book) => (
              <div key={book.id} className="glass p-4 rounded-[1.5rem] hover:-translate-y-2 hover:shadow-lg transition-all duration-300 flex flex-col">
                <a href={book.url} target="_blank" rel="noreferrer" className="block w-full h-48 bg-slate-100 rounded-xl mb-4 overflow-hidden shadow-inner group">
                  {book.image_url ? (
                    <img src={book.image_url} alt={book.title} className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"><BookOpen className="w-12 h-12 text-slate-300" /></div>
                  )}
                </a>
                <a href={book.url} target="_blank" rel="noreferrer" className="hover:text-primary transition-colors">
                  <h3 className="font-bold text-lg mb-1 truncate">{book.title}</h3>
                </a>
                <p className="text-primary text-sm mb-3 truncate">{book.rating} Star Rating</p>
                <div className="flex justify-between items-center mt-auto pt-4 border-t border-slate-100">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold">₹{book.price}</span>
                    <span className="text-[10px] uppercase text-slate-500 font-bold">{book.purchases_count} Sales</span>
                  </div>
                  <button onClick={(e) => buyBook(e, book.id)} className="bg-green-500 hover:bg-green-600 text-white px-4 py-1.5 rounded-lg font-bold text-sm transition-colors shadow">Buy</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// --- Settings Component ---
function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto mt-6 animate-in fade-in duration-500">
      <h2 className="text-3xl font-bold mb-8">System Configuration</h2>
      
      <div className="grid gap-6">
        <div className="glass p-8 rounded-3xl border-slate-200">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-3"><Settings className="text-primary w-6 h-6"/> LLM Preferences</h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-500 mb-2">Primary Model Provider</label>
              <select className="w-full bg-background border border-slate-300 rounded-xl px-4 py-3 text-slate-900 outline-none focus:border-primary">
                <option>Google - Gemini 2.5 Flash (Configured in .env)</option>
                <option>Local (LM Studio) - Meta LLaMA 3 8B</option>
                <option>OpenAI - GPT-4o</option>
                <option>Anthropic - Claude 3.5</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-500 mb-2">Embedding Model (ChromaDB)</label>
              <select className="w-full bg-background border border-slate-300 rounded-xl px-4 py-3 text-slate-900 outline-none focus:border-primary">
                <option>all-MiniLM-L6-v2</option>
                <option>text-embedding-3-small</option>
              </select>
            </div>
          </div>
        </div>

        <div className="glass p-8 rounded-3xl border-slate-200">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-3"><Database className="text-secondary w-6 h-6"/> Scraper Configuration</h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-500 mb-2">Target URL Endpoint</label>
              <input type="text" value="https://books.toscrape.com/" readOnly className="w-full bg-surface border border-slate-200 rounded-xl px-4 py-3 text-slate-500 outline-none" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- App Layout ---
function App() {
  const [activeTab, setActiveTab] = useState(window.location.pathname);
  // Default user as Admin so everything is visible
  const user = { name: 'Karthik Reddy', role: 'admin' };

  return (
    <BrowserRouter>
      <div className="flex h-screen w-full relative bg-background overflow-hidden text-textMain selection:bg-primary/30">
        {/* Sidebar */}
        <aside className="w-[280px] glass m-5 rounded-[2rem] flex flex-col z-10 border-slate-200 shadow-2xl relative">
          <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent rounded-[2rem] pointer-events-none"></div>
          
          <div className="p-8 pb-6">
            <h1 className="text-2xl font-black tracking-tight flex items-center gap-3">
              <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-sm shadow-[0_5px_15px_rgba(79,70,229,0.3)] border border-slate-300">NB</span>
              NSR BOOKS
            </h1>
          </div>
          
          <nav className="flex-1 px-4 py-2 space-y-2">
            {[
              { path: '/', name: 'Dashboard', icon: <Home className="w-5 h-5" /> },
              { path: '/library', name: 'Book Catalog', icon: <LibraryIcon className="w-5 h-5" /> },
              { path: '/chat', name: 'NSR AI Assistant', icon: <MessageSquare className="w-5 h-5" /> },
              { path: '/scraper', name: 'Update Books', icon: <Database className="w-5 h-5" /> },
              { path: '/settings', name: 'Settings', icon: <Settings className="w-5 h-5" /> },
            ].map((item) => (
              <Link 
                key={item.path} 
                to={item.path}
                onClick={() => setActiveTab(item.path)}
                className={`flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 ${
                  activeTab === item.path || (item.path === '/' && activeTab === '')
                    ? 'bg-slate-200 text-slate-900 shadow-[inset_0_1px_0_rgba(255,255,255,0.1)] border border-slate-200 relative overflow-hidden' 
                    : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                {activeTab === item.path && <div className="absolute left-0 top-0 w-1 h-full bg-primary shadow-[0_0_10px_theme('colors.primary')]"></div>}
                
                <div className={`${activeTab === item.path ? 'text-primary drop-shadow-[0_0_8px_rgba(79,70,229,0.5)]' : ''} transition-all`}>
                  {item.icon}
                </div>
                <span className="font-semibold text-sm tracking-wide">{item.name}</span>
              </Link>
            ))}
          </nav>
          
          <div className="p-6 mt-auto">
            <div className="p-4 bg-slate-100 rounded-2xl border border-slate-200 flex items-center gap-4 shadow-inner">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white text-sm shadow-md ring-2 ring-white/10">
                KR
              </div>
              <div className="flex-1">
                <p className="font-bold text-sm tracking-wide">Karthik Reddy</p>
                <p className="text-[10px] text-green-600 flex items-center gap-1.5 font-bold tracking-widest uppercase mt-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block animate-pulse"></span> 
                  Admin Mode
                </p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8 lg:p-10 overflow-y-auto z-10 custom-scrollbar">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/library" element={<Library />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/scraper" element={<Scraper />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
