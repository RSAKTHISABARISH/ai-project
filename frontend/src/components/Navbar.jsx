import React from 'react';
import { 
  LayoutDashboard, 
  Database, 
  SearchCode, 
  Sparkles, 
  ShieldCheck, 
  BookOpen, 
  LineChart,
  Layers,
  Wand2,
  CheckCircle2
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, health, onSeedDemo, onLoadInc052, loadingDemo }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'ingestion', label: 'Ingestion & Events', icon: Database },
    { id: 'investigation', label: 'Investigation', icon: SearchCode },
    { id: 'ai-recommend', label: 'AI Synthesis', icon: Sparkles },
    { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
    { id: 'runbooks', label: 'Runbook Base', icon: BookOpen },
    { id: 'experiment', label: 'Metrics & Errors', icon: LineChart },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-md border-b border-pink-100 shadow-sm shadow-pink-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 via-pink-500 to-purple-600 flex items-center justify-center text-white shadow-md shadow-pink-500/20">
              <Layers className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold font-['Outfit'] tracking-tight bg-gradient-to-r from-rose-700 via-pink-600 to-purple-700 bg-clip-text text-transparent">
                  Fix2Runbook
                </span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 border border-rose-200">
                  ERP SRE
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Evidence-Driven ERP Maintenance Knowledge Capture
              </p>
            </div>
          </div>

          {/* Quick Demo Action Buttons & System Mode */}
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-pink-50/70 border border-pink-200/80 text-xs text-rose-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="font-medium truncate max-w-[200px]">
                {health?.mode || 'Deterministic / Demo Mode'}
              </span>
            </div>

            <button
              onClick={onLoadInc052}
              disabled={loadingDemo}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 rounded-lg shadow-sm shadow-rose-200 transition-all duration-150 active:scale-95 disabled:opacity-50"
              title="Load featured scenario INC-052 / PR-142"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span>Load INC-052 Demo</span>
            </button>

            <button
              onClick={onSeedDemo}
              disabled={loadingDemo}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg transition-all duration-150"
              title="Reset & Seed 30+ ERP Incidents & 100+ Events"
            >
              <Database className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Reset Seed</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex space-x-1 sm:space-x-2 overflow-x-auto py-2 border-t border-pink-50 no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg whitespace-nowrap transition-all duration-150 ${
                  isActive
                    ? 'bg-rose-500 text-white shadow-sm shadow-rose-300 font-semibold'
                    : 'text-slate-600 hover:text-rose-600 hover:bg-rose-50/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-rose-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

      </div>
    </header>
  );
}
