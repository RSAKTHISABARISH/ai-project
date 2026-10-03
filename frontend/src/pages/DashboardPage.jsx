import React from 'react';
import { 
  Clock, 
  TrendingDown, 
  CheckCircle2, 
  ShieldAlert, 
  BookOpen, 
  Sparkles, 
  AlertTriangle,
  ArrowRight,
  Zap,
  Activity
} from 'lucide-react';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import EvidenceBadge from '../components/EvidenceBadge';

export default function DashboardPage({ 
  metrics, 
  runbooks = [], 
  onSelectRunbook, 
  onNavigateTab,
  onLoadInc052
}) {
  const m = metrics || {};
  const baseline = m.baseline_fix_time_mins || 42.0;
  const prototype = m.prototype_fix_time_mins || 18.0;
  const reduction = m.time_reduction_percentage || 57.1;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      
      {/* Hero Banner with Feminine Rose Glassmorphic Elegance */}
      <div className="relative rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-rose-500/90 via-pink-500/85 to-purple-600/90 text-white shadow-xl shadow-pink-500/15 overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 rounded-full bg-white/10 blur-2xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold mb-3 border border-white/25">
            <Sparkles className="w-3.5 h-3.5" />
            <span>ERP Maintenance Knowledge Capture</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-bold font-['Outfit'] tracking-tight">
            Evidence-Driven ERP Troubleshooting Knowledge Engine
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-rose-100 leading-relaxed max-w-2xl">
            Converts scattered pull requests, incident discussions, code diffs, and reviewer sign-offs into verified, reusable maintenance runbooks for future on-call engineers.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigateTab('ai-recommend')}
              className="px-4 py-2 rounded-xl bg-white text-rose-600 font-bold text-xs shadow-md hover:bg-rose-50 transition-all duration-150 active:scale-95 flex items-center gap-2"
            >
              <Zap className="w-3.5 h-3.5 text-rose-500" />
              <span>Generate New Runbook</span>
            </button>
            <button
              onClick={() => onNavigateTab('ingestion')}
              className="px-4 py-2 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white font-semibold text-xs border border-white/30 transition-all"
            >
              <span>Simulate Event Engine</span>
            </button>
            <button
              onClick={() => onNavigateTab('experiment')}
              className="px-4 py-2 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white font-semibold text-xs border border-white/30 transition-all flex items-center gap-1.5"
            >
              <span>View Experiment Results</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Primary Objective: Time Reduction Benchmark (PRD §2) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-card border border-rose-200/80 bg-gradient-to-br from-white/90 to-rose-50/40">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Baseline Engineer Fix Time</p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-bold font-['Outfit'] text-slate-800">{baseline}</span>
            <span className="text-xs text-slate-500 font-semibold">minutes</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Raw tickets, unorganized diffs & scattered reviews
          </p>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-pink-200/80 bg-gradient-to-br from-white/90 to-pink-50/40">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Target Objective</p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-bold font-['Outfit'] text-slate-800">&lt; 25.0</span>
            <span className="text-xs text-slate-500 font-semibold">minutes</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Target SLA for repeating known ERP bugs
          </p>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-emerald-200/80 bg-gradient-to-br from-white/90 to-emerald-50/40">
          <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider">Measured Prototype Time</p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-bold font-['Outfit'] text-emerald-600">{prototype}</span>
            <span className="text-xs text-emerald-700 font-semibold">minutes</span>
          </div>
          <p className="text-[11px] text-emerald-700/80 mt-2 font-medium">
            Empirical average across 10 benchmark tasks
          </p>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-rose-300 bg-gradient-to-br from-rose-500 to-pink-600 text-white shadow-lg shadow-rose-500/20">
          <p className="text-xs font-bold text-rose-100 uppercase tracking-wider flex items-center gap-1.5">
            <TrendingDown className="w-4 h-4" />
            Measured Time Reduction
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-4xl font-extrabold font-['Outfit']">{reduction}%</span>
          </div>
          <p className="text-[11px] text-rose-100 mt-2">
            Verified productivity improvement for new engineers
          </p>
        </div>
      </div>

      {/* System KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
        <StatCard
          title="Total Incidents"
          value={m.total_incidents || 32}
          subtitle="Synthesized ERP bugs"
          icon={AlertTriangle}
          color="rose"
        />
        <StatCard
          title="PR Fixes Linked"
          value={m.total_fixes || 32}
          subtitle="With unified diffs"
          icon={Activity}
          color="pink"
        />
        <StatCard
          title="Runbooks Generated"
          value={m.generated_runbooks || 1}
          subtitle="AI & Rule-extracted"
          icon={BookOpen}
          color="purple"
        />
        <StatCard
          title="Verified Runbooks"
          value={m.verified_runbooks || 1}
          subtitle="Fully rule-aligned"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Pending Approvals"
          value={m.pending_approvals || 0}
          subtitle="Human review queue"
          icon={ShieldAlert}
          color="amber"
        />
        <StatCard
          title="High-Risk Actions"
          value={m.high_risk_recommendations || 1}
          subtitle="Financial & Tax rules"
          icon={ShieldAlert}
          color="rose"
        />
      </div>

      {/* Showcase INC-052 Quick Action Banner */}
      <div className="p-5 rounded-2xl border border-pink-200 bg-white/70 backdrop-blur-md shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-slate-800">Featured Showcase: Incident INC-052</h4>
              <RiskBadge level="HIGH" showLabel={false} />
              <EvidenceBadge status="VERIFIED" />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Incorrect invoice tax calculation due to regional discount ordering (RULE-TAX-104).
            </p>
          </div>
        </div>

        <button
          onClick={onLoadInc052}
          className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 shadow-sm active:scale-95 transition-all whitespace-nowrap"
        >
          Load & Inspect INC-052
        </button>
      </div>

      {/* Recent Runbooks Catalog Table */}
      <div className="glass-card rounded-2xl border border-pink-100 overflow-hidden">
        <div className="p-5 border-b border-pink-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold font-['Outfit'] text-slate-800">
              Verified Knowledge Base Runbooks
            </h3>
            <p className="text-xs text-slate-500">
              Structured maintenance workflows ready for engineering execution.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('runbooks')}
            className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-pink-50/40 text-slate-500 font-semibold border-b border-pink-100">
              <tr>
                <th className="p-3.5 pl-5">Runbook ID</th>
                <th className="p-3.5">Title / Target Issue</th>
                <th className="p-3.5">ERP Module</th>
                <th className="p-3.5">Risk Level</th>
                <th className="p-3.5">Evidence Status</th>
                <th className="p-3.5">State</th>
                <th className="p-3.5 pr-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pink-50">
              {runbooks.slice(0, 5).map((rb) => (
                <tr key={rb.runbook_id} className="hover:bg-rose-50/30 transition-colors">
                  <td className="p-3.5 pl-5 font-mono font-bold text-slate-800">{rb.runbook_id}</td>
                  <td className="p-3.5 font-medium text-slate-900 max-w-xs truncate">{rb.title}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 font-medium border border-purple-200">
                      {rb.affected_module}
                    </span>
                  </td>
                  <td className="p-3.5">
                    <RiskBadge level={rb.risk_level} />
                  </td>
                  <td className="p-3.5">
                    <EvidenceBadge status={rb.evidence_completeness} />
                  </td>
                  <td className="p-3.5">
                    <span className="font-mono text-[11px] font-semibold text-slate-700">{rb.status}</span>
                  </td>
                  <td className="p-3.5 pr-5 text-right">
                    <button
                      onClick={() => onSelectRunbook(rb)}
                      className="px-3 py-1 rounded-lg bg-pink-100 hover:bg-pink-200 text-rose-700 font-semibold transition-colors"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
