import os

app_path = r"c:\Users\Karthik Reddy\OneDrive\Desktop\KARTHIK\coding vs\project  Book ai automation\frontend\src\App.jsx"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove LoginPage component
login_start = content.find("// --- Login Component ---")
dashboard_start = content.find("// --- Dashboard Component ---")
if login_start != -1 and dashboard_start != -1:
    content = content[:login_start] + content[dashboard_start:]

# 2. Update App component to remove auth logic and default to Admin
app_start = content.find("// --- App Layout ---")
if app_start != -1:
    new_app = """// --- App Layout ---
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
"""
    content = content[:app_start] + new_app

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Login system removed from App.jsx")
