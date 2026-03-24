"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import { 
  User, LogOut, TrendingUp, Users, DollarSign, Plus, 
  Search, Filter, ChevronRight, LayoutDashboard, 
  Briefcase, MessageSquare, AlertCircle, CheckCircle2,
  Clock, Sparkles
} from "lucide-react";

const API_URL = "http://34.133.123.104:8000/api";

// Oatey Brand Colors
const COLORS = {
  brown: "#5c4033",
  cream: "#f5f5dc",
  yellow: "#f9d71c",
  dark: "#2d1b0d",
  light: "#fffaf0",
  accent: "#d97706",
  muted: "#a8a29e"
};

const CHART_COLORS = ['#5c4033', '#d97706', '#f9d71c', '#8b4513', '#cd853f'];

export default function Home() {
  const [user, setUser] = useState<{ role: string; name: string } | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [leads, setLeads] = useState<any[]>([]);
  const [metrics, setMetrics] = useState({ total_pipeline: 0, active_leads: 0, closed_won: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("dashboard");

  const [showAddModal, setShowAddModal] = useState(false);
  const [newLead, setNewLead] = useState({ lead_name: "", category: "FMCG", salesperson: "", po_value_expected: 0 });

  // AI Pitch state
  const [selectedLeadForPitch, setSelectedLeadForPitch] = useState<any>(null);
  const [aiPitch, setAiPitch] = useState("");
  const [generatingPitch, setGeneratingPitch] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { username, password });
      setUser(res.data);
      fetchData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchData = async (currentUser = user) => {
    if (!currentUser) return;
    try {
      const leadsRes = await axios.get(`${API_URL}/leads`, {
        params: currentUser.role === "Salesperson" ? { salesperson: currentUser.name } : {}
      });
      setLeads(leadsRes.data);
      
      const metricsRes = await axios.get(`${API_URL}/metrics`);
      setMetrics(metricsRes.data);
    } catch (err) {
      console.error("Failed to fetch data", err);
    }
  };

  const handleAddLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/leads`, { ...newLead, salesperson: user?.name });
      setShowAddModal(false);
      setNewLead({ lead_name: "", category: "FMCG", salesperson: "", po_value_expected: 0 });
      fetchData();
    } catch (err) {
      console.error("Failed to add lead", err);
    }
  };

  const generatePitch = async (lead: any) => {
    setSelectedLeadForPitch(lead);
    setGeneratingPitch(true);
    setAiPitch("");
    try {
      const res = await axios.post(`${API_URL}/ai/pitch`, {
        lead_name: lead.lead_name,
        category: lead.category,
        comments: lead.comments || "No comments yet",
        po_value: lead.po_value_expected || 0
      });
      setAiPitch(res.data.pitch);
    } catch (err) {
      setAiPitch("Failed to generate AI pitch. Please check your API configuration.");
    } finally {
      setGeneratingPitch(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#fffaf0] font-sans">
        <div className="max-w-md w-full p-10 bg-white rounded-3xl shadow-2xl border border-[#f5f5dc]">
          <div className="text-center mb-10">
            <div className="flex justify-center mb-4">
              <div className="bg-[#5c4033] p-4 rounded-2xl shadow-lg">
                <span className="text-[#f9d71c] text-3xl font-black tracking-tighter">OATEY</span>
              </div>
            </div>
            <h2 className="text-3xl font-extrabold text-[#2d1b0d]">Sales Pulse</h2>
            <p className="text-stone-500 mt-3 font-medium text-sm">Empowering plant-based dairy sales excellence</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="relative">
              <label className="text-xs font-bold text-[#5c4033] uppercase tracking-widest mb-1.5 block ml-1">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                  <User size={18} />
                </span>
                <input
                  type="text"
                  required
                  className="block w-full pl-11 pr-4 py-3.5 bg-stone-50 border border-stone-200 rounded-xl focus:ring-2 focus:ring-[#f9d71c] focus:border-[#f9d71c] transition-all outline-none text-[#2d1b0d] font-medium"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>
            
            <div className="relative">
              <label className="text-xs font-bold text-[#5c4033] uppercase tracking-widest mb-1.5 block ml-1">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                  <Clock size={18} />
                </span>
                <input
                  type="password"
                  required
                  className="block w-full pl-11 pr-4 py-3.5 bg-stone-50 border border-stone-200 rounded-xl focus:ring-2 focus:ring-[#f9d71c] focus:border-[#f9d71c] transition-all outline-none text-[#2d1b0d] font-medium"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg flex items-start animate-shake">
                <AlertCircle className="text-red-500 mr-2 flex-shrink-0 mt-0.5" size={16} />
                <p className="text-red-700 text-xs font-semibold leading-tight">{error}</p>
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-4 px-6 border border-transparent rounded-2xl shadow-lg text-base font-bold text-[#2d1b0d] bg-[#f9d71c] hover:bg-[#e6c619] active:scale-95 transform transition-all focus:outline-none disabled:opacity-50 disabled:scale-100"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-[#2d1b0d] border-t-transparent rounded-full animate-spin mr-2"></div>
              ) : null}
              {loading ? "Verifying..." : "Access Dashboard"}
            </button>
            
            <div className="mt-8 pt-6 border-t border-stone-100">
              <p className="text-[10px] text-center text-stone-400 font-bold uppercase tracking-[0.2em]">Authorized Personnel Only</p>
              <div className="flex justify-center gap-4 mt-3">
                <span className="text-[10px] bg-stone-100 text-stone-500 px-2 py-1 rounded">Admin</span>
                <span className="text-[10px] bg-stone-100 text-stone-500 px-2 py-1 rounded">Sales</span>
                <span className="text-[10px] bg-stone-100 text-stone-500 px-2 py-1 rounded">Operations</span>
              </div>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Filter leads based on search
  const filteredLeads = leads.filter(lead => 
    lead.lead_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.salesperson?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group leads by category for charts
  const chartData = leads.reduce((acc: any[], lead: any) => {
    const existing = acc.find((item: any) => item.category === lead.category);
    if (existing) {
      existing.value += lead.po_value_expected || 0;
    } else {
      acc.push({ category: lead.category, value: lead.po_value_expected || 0 });
    }
    return acc;
  }, []);

  return (
    <div className="min-h-screen bg-[#fffaf0] text-[#2d1b0d] flex font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-72 bg-[#5c4033] flex-shrink-0 hidden lg:flex flex-col shadow-2xl relative z-10">
        <div className="p-8">
          <div className="bg-[#f9d71c] p-3 rounded-xl inline-block shadow-lg mb-8">
            <span className="text-[#2d1b0d] text-2xl font-black tracking-tighter">OATEY</span>
          </div>
          <div className="space-y-2">
            <NavItem 
              icon={<LayoutDashboard size={20} />} 
              label="Overview" 
              active={activeTab === 'dashboard'} 
              onClick={() => setActiveTab('dashboard')} 
            />
            <NavItem 
              icon={<Briefcase size={20} />} 
              label="Leads Pipe" 
              active={activeTab === 'leads'} 
              onClick={() => setActiveTab('leads')} 
            />
            {user.role === 'Leadership' && (
              <NavItem 
                icon={<TrendingUp size={20} />} 
                label="Analytics" 
                active={activeTab === 'analytics'} 
                onClick={() => setActiveTab('analytics')} 
              />
            )}
          </div>
        </div>
        
        <div className="mt-auto p-8 pt-0">
          <div className="bg-[#2d1b0d]/30 rounded-2xl p-5 border border-white/5 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#f9d71c] flex items-center justify-center font-bold text-[#2d1b0d]">
                {user.name.charAt(0)}
              </div>
              <div className="overflow-hidden">
                <p className="text-white text-sm font-bold truncate">{user.name}</p>
                <p className="text-[#f9d71c] text-[10px] font-black uppercase tracking-widest">{user.role}</p>
              </div>
            </div>
            <button 
              onClick={() => setUser(null)}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-white/10 hover:bg-white/20 text-white text-sm font-bold rounded-xl transition-all"
            >
              <LogOut size={16} /> Log Out
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-20 bg-white border-b border-[#f5f5dc] flex items-center justify-between px-10 flex-shrink-0">
          <div>
            <h2 className="text-xl font-extrabold text-[#2d1b0d]">
              {activeTab === 'dashboard' ? 'Market Overview' : activeTab === 'leads' ? 'Lead Pipeline' : 'Performance Analytics'}
            </h2>
            <p className="text-xs text-stone-400 font-bold uppercase tracking-widest mt-1">
              Live updates for {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="relative group hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400 group-focus-within:text-[#5c4033] transition-colors" size={18} />
              <input 
                type="text" 
                placeholder="Search leads, brands..."
                className="pl-10 pr-4 py-2.5 bg-stone-50 border border-stone-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-[#f5f5dc] w-64 transition-all"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button className="p-2.5 bg-stone-50 rounded-xl border border-stone-100 text-[#5c4033] hover:bg-stone-100 transition-all relative">
              <div className="absolute top-2 right-2 w-2 h-2 bg-[#d97706] rounded-full border-2 border-white"></div>
              <Sparkles size={20} />
            </button>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-10 bg-[#fffaf0]/50">
          {activeTab === 'dashboard' && (
            <div className="space-y-10">
              {/* KPIs */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <KPICard 
                  title="Pipeline Value" 
                  value={`₹${metrics.total_pipeline.toLocaleString()}`} 
                  icon={<DollarSign size={24} />} 
                  color="blue"
                  trend="+12.5% from last month"
                />
                <KPICard 
                  title="Active Opportunities" 
                  value={metrics.active_leads.toString()} 
                  icon={<Users size={24} />} 
                  color="amber"
                  trend="8 new since yesterday"
                />
                <KPICard 
                  title="Revenue Secured" 
                  value={`₹${metrics.closed_won.toLocaleString()}`} 
                  icon={<CheckCircle2 size={24} />} 
                  color="green"
                  trend="45.2% win rate"
                />
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-3 gap-10">
                {/* Visuals */}
                <div className="xl:col-span-2 bg-white p-8 rounded-[2rem] shadow-sm border border-[#f5f5dc]">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-lg font-extrabold flex items-center gap-2">
                      <LayoutDashboard size={20} className="text-[#5c4033]" />
                      Revenue Distribution by Vertical
                    </h3>
                    <div className="flex gap-2">
                      <span className="px-3 py-1 bg-stone-50 rounded-full text-[10px] font-black uppercase tracking-widest text-stone-500">Weekly</span>
                    </div>
                  </div>
                  <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f5f5dc" vertical={false} />
                        <XAxis 
                          dataKey="category" 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{ fill: '#a8a29e', fontSize: 12, fontWeight: 700 }} 
                        />
                        <YAxis 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{ fill: '#a8a29e', fontSize: 12, fontWeight: 700 }}
                          tickFormatter={(value) => `₹${value/1000}k`}
                        />
                        <Tooltip 
                          cursor={{ fill: '#fffaf0' }}
                          contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', fontWeight: 'bold' }}
                          formatter={(value: any) => [`₹${Number(value).toLocaleString()}`, 'Pipeline Value']}
                        />
                        <Bar dataKey="value" radius={[10, 10, 0, 0]} barSize={40}>
                          {chartData.map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Side Actions/Stats */}
                <div className="space-y-8">
                  <div className="bg-[#5c4033] p-8 rounded-[2rem] shadow-lg text-white relative overflow-hidden">
                    <div className="relative z-10">
                      <h3 className="text-lg font-extrabold mb-2">New Vertical Added</h3>
                      <p className="text-white/70 text-sm mb-6">Millet Milk is seeing 40% higher engagement in Tier 2 cities.</p>
                      <button className="px-5 py-2.5 bg-[#f9d71c] text-[#2d1b0d] rounded-xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-105 transition-transform">
                        Explore Insights
                      </button>
                    </div>
                    <div className="absolute top-[-20px] right-[-20px] w-32 h-32 bg-white/5 rounded-full blur-3xl"></div>
                  </div>
                  
                  <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-[#f5f5dc]">
                    <h3 className="text-sm font-black uppercase tracking-[0.2em] text-stone-400 mb-6">Recent Wins</h3>
                    <div className="space-y-5">
                      {leads.filter(l => l.status === 'Closed Won').slice(0, 3).map((lead, i) => (
                        <div key={i} className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-green-600 font-bold">
                            <CheckCircle2 size={18} />
                          </div>
                          <div>
                            <p className="text-xs font-bold leading-none mb-1">{lead.lead_name}</p>
                            <p className="text-[10px] text-stone-400 font-bold uppercase tracking-widest">₹{lead.po_value_expected?.toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'leads' && (
            <div className="space-y-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="bg-[#5c4033] p-2 rounded-lg text-white">
                    <Briefcase size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-extrabold">Opportunities</h3>
                    <p className="text-xs text-stone-400 font-bold">Showing {filteredLeads.length} active leads</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-[#f5f5dc] rounded-xl text-xs font-bold text-[#5c4033] hover:bg-stone-50 shadow-sm">
                    <Filter size={16} /> Filters
                  </button>
                  {user.role === 'Salesperson' && (
                    <button 
                      onClick={() => setShowAddModal(true)}
                      className="flex items-center gap-2 px-6 py-2.5 bg-[#f9d71c] text-[#2d1b0d] rounded-xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-105 transition-transform"
                    >
                      <Plus size={16} /> Create Lead
                    </button>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-[2rem] shadow-sm border border-[#f5f5dc] overflow-hidden">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-stone-50">
                      <th className="text-left px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">Lead Detail</th>
                      <th className="text-left px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">Category</th>
                      <th className="text-left px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">Status</th>
                      <th className="text-left px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">Pipeline Value</th>
                      <th className="text-center px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">AI Assistant</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-50">
                    {filteredLeads.map((lead, idx) => (
                      <tr key={idx} className="group hover:bg-[#fffaf0] transition-all cursor-pointer">
                        <td className="px-8 py-6">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-stone-100 flex items-center justify-center font-bold text-[#5c4033] group-hover:bg-[#5c4033] group-hover:text-white transition-all">
                              {lead.lead_name?.charAt(0)}
                            </div>
                            <div>
                              <p className="text-sm font-bold text-[#2d1b0d]">{lead.lead_name}</p>
                              <p className="text-[10px] text-stone-400 font-medium">Updated: {lead.last_updated?.split(' ')[0]}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-8 py-6">
                          <span className="px-3 py-1 bg-stone-50 rounded-lg text-[10px] font-black uppercase tracking-widest text-[#5c4033]">
                            {lead.category}
                          </span>
                        </td>
                        <td className="px-8 py-6">
                          <StatusBadge status={lead.status} />
                        </td>
                        <td className="px-8 py-6">
                          <p className="text-sm font-bold">₹{(lead.po_value_expected || 0).toLocaleString()}</p>
                          <p className="text-[10px] text-stone-400 font-bold uppercase tracking-widest">{lead.priority || 'Medium'} Priority</p>
                        </td>
                        <td className="px-8 py-6 text-center">
                          <button 
                            onClick={() => generatePitch(lead)}
                            className="p-2 bg-[#f9d71c]/10 text-[#5c4033] rounded-xl hover:bg-[#f9d71c] transition-all"
                            title="Generate AI Strategy"
                          >
                            <Sparkles size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* AI Pitch Modal */}
      {selectedLeadForPitch && (
        <div className="fixed z-50 inset-0 overflow-y-auto" aria-labelledby="ai-modal-title" role="dialog" aria-modal="true">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-[#2d1b0d]/80 backdrop-blur-sm transition-opacity" onClick={() => setSelectedLeadForPitch(null)}></div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-[2.5rem] text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
              <div className="relative">
                <div className="h-32 bg-[#5c4033] p-10">
                  <h3 className="text-2xl font-black text-[#f9d71c] flex items-center gap-3">
                    <Sparkles size={28} /> AI Sales Strategist
                  </h3>
                  <p className="text-white/60 text-sm font-medium mt-1 uppercase tracking-widest">Custom Pitch for {selectedLeadForPitch.lead_name}</p>
                </div>
                <button 
                  onClick={() => setSelectedLeadForPitch(null)}
                  className="absolute top-6 right-8 text-white/50 hover:text-white transition-colors"
                >
                  <AlertCircle size={24} className="rotate-45" />
                </button>
                
                <div className="px-10 py-8 max-h-[60vh] overflow-y-auto">
                  {generatingPitch ? (
                    <div className="flex flex-col items-center justify-center py-20 space-y-6">
                      <div className="relative">
                        <div className="w-16 h-16 border-4 border-[#f9d71c]/20 border-t-[#f9d71c] rounded-full animate-spin"></div>
                        <Sparkles className="absolute inset-0 m-auto text-[#f9d71c] animate-pulse" size={24} />
                      </div>
                      <p className="text-stone-400 font-bold uppercase tracking-[0.2em] text-[10px]">Analyzing market data & generating strategy...</p>
                    </div>
                  ) : (
                    <div className="prose prose-stone max-w-none">
                      <div className="whitespace-pre-wrap text-stone-700 leading-relaxed font-medium">
                        {aiPitch || "AI strategy generation failed. Please try again."}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="bg-stone-50 px-10 py-6 border-t border-stone-100 flex justify-end gap-3">
                  <button 
                    onClick={() => setSelectedLeadForPitch(null)}
                    className="px-6 py-2.5 bg-white border border-stone-200 rounded-xl text-xs font-black uppercase tracking-widest text-[#5c4033] hover:bg-stone-100 transition-all shadow-sm"
                  >
                    Dismiss
                  </button>
                  <button 
                    onClick={() => window.print()}
                    className="px-6 py-2.5 bg-[#5c4033] text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-105 transition-transform"
                  >
                    Print Strategy
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Lead Modal */}
      {showAddModal && (
        <div className="fixed z-50 inset-0 overflow-y-auto" role="dialog" aria-modal="true">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-[#2d1b0d]/60 backdrop-blur-sm transition-opacity" onClick={() => setShowAddModal(false)}></div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-[2.5rem] text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <form onSubmit={handleAddLead}>
                <div className="px-10 py-10">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-12 h-12 bg-[#f9d71c] rounded-2xl flex items-center justify-center text-[#2d1b0d]">
                      <Plus size={24} />
                    </div>
                    <div>
                      <h3 className="text-xl font-black text-[#2d1b0d]">Capture New Lead</h3>
                      <p className="text-xs text-stone-400 font-bold uppercase tracking-widest">Growing the Oatey community</p>
                    </div>
                  </div>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="text-[10px] font-black uppercase tracking-widest text-[#5c4033] mb-2 block ml-1">Brand/Company Name</label>
                      <input required type="text" placeholder="e.g. Starbuck's Coffee" className="block w-full px-4 py-3.5 bg-stone-50 border border-stone-100 rounded-2xl focus:ring-2 focus:ring-[#f9d71c] outline-none font-bold"
                        value={newLead.lead_name} onChange={e => setNewLead({...newLead, lead_name: e.target.value})} />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[10px] font-black uppercase tracking-widest text-[#5c4033] mb-2 block ml-1">Market Vertical</label>
                        <select className="block w-full px-4 py-3.5 bg-stone-50 border border-stone-100 rounded-2xl focus:ring-2 focus:ring-[#f9d71c] outline-none font-bold appearance-none cursor-pointer"
                          value={newLead.category} onChange={e => setNewLead({...newLead, category: e.target.value})}>
                          <option>FMCG</option>
                          <option>HORECA</option>
                          <option>E-COMMERCE</option>
                          <option>MODERN TRADE</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-[10px] font-black uppercase tracking-widest text-[#5c4033] mb-2 block ml-1">Est. Value (₹)</label>
                        <input required type="number" placeholder="50000" className="block w-full px-4 py-3.5 bg-stone-50 border border-stone-100 rounded-2xl focus:ring-2 focus:ring-[#f9d71c] outline-none font-bold"
                          value={newLead.po_value_expected} onChange={e => setNewLead({...newLead, po_value_expected: parseFloat(e.target.value)})} />
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-stone-50 px-10 py-8 border-t border-stone-100 flex justify-end gap-3">
                  <button type="button" onClick={() => setShowAddModal(false)} className="px-6 py-3 bg-white border border-stone-200 rounded-xl text-xs font-black uppercase tracking-widest text-[#5c4033] hover:bg-stone-100 transition-all">
                    Discard
                  </button>
                  <button type="submit" className="px-8 py-3 bg-[#f9d71c] text-[#2d1b0d] rounded-xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-105 active:scale-95 transition-all">
                    Secure Lead
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Sub-components for better organization
function NavItem({ icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${
        active 
          ? 'bg-[#f9d71c] text-[#2d1b0d] shadow-xl shadow-[#2d1b0d]/50 translate-x-1' 
          : 'text-white/60 hover:text-white hover:bg-white/5'
      }`}
    >
      <span className={active ? 'text-[#2d1b0d]' : 'text-stone-400'}>{icon}</span>
      <span className="text-sm font-black uppercase tracking-widest">{label}</span>
      {active && <ChevronRight className="ml-auto" size={16} />}
    </button>
  );
}

function KPICard({ title, value, icon, color, trend }: { title: string, value: string, icon: any, color: string, trend: string }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    amber: 'bg-[#f9d71c]/10 text-[#5c4033]',
    green: 'bg-green-50 text-green-600'
  }[color as 'blue' | 'amber' | 'green'];
  
  return (
    <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-[#f5f5dc] group hover:scale-[1.02] transition-all duration-500">
      <div className="flex items-center gap-4 mb-6">
        <div className={`p-4 rounded-2xl ${colors} group-hover:scale-110 transition-transform`}>
          {icon}
        </div>
        <div>
          <h4 className="text-[10px] font-black text-stone-400 uppercase tracking-[0.2em] mb-1">{title}</h4>
          <p className="text-2xl font-black text-[#2d1b0d] tracking-tighter">{value}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
        <p className="text-[10px] font-black text-stone-400 uppercase tracking-widest">{trend}</p>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const configs = {
    'Closed Won': 'bg-green-50 text-green-700 border-green-100',
    'New': 'bg-blue-50 text-blue-700 border-blue-100',
    'Proposal Sent': 'bg-amber-50 text-amber-700 border-amber-100',
    'Negotiation': 'bg-purple-50 text-purple-700 border-purple-100'
  }[status as string] || 'bg-stone-50 text-stone-600 border-stone-100';

  return (
    <span className={`px-3 py-1.5 rounded-xl border text-[10px] font-black uppercase tracking-widest ${configs}`}>
      {status || 'Draft'}
    </span>
  );
}
