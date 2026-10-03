import React, { useState, useEffect } from 'react';
import { 
  Search, 
  BookOpen, 
  Copy, 
  Check, 
  Filter, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import EvidenceBadge from '../components/EvidenceBadge';

export default function RunbooksPage({ onSelectRunbook, onShowToast }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [runbooks, setRunbooks] = useState([]);
  const [selectedModule, setSelectedModule] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const sampleSearches = [
    'invoice tax calculation',
    'INC-052',
    'regional discount',
    'RULE-TAX-104',
    'inventory reservation',
    'payment gateway'
  ];

  const fetchRunbooks = async (query = searchQuery) => {
    try {
      setLoading(true);
      if (query.trim()) {
        const searchRes = await api.searchRunbooks(query.trim());
        setRunbooks((searchRes.results || []).map(r => r.runbook));
      } else {
        const data = await api.getRunbooks();
        setRunbooks(data || []);
      }
    } catch (err) {
      onShowToast({ type: 'error', title: 'Search Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRunbooks();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRunbooks(searchQuery);
  };

  const handleSampleClick = (term) => {
    setSearchQuery(term);
    fetchRunbooks(term);
  };

  const handleCopy = (e, rb) => {
    e.stopPropagation();
    navigator.clipboard.writeText(
      `RUNBOOK ${rb.runbook_id}: ${rb.title}\n\nFIX PROCEDURE:\n${(rb.fix_procedure || []).join('\n')}`
    );
    setCopiedId(rb.runbook_id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filter runbooks by module and status
  const filteredRunbooks = runbooks.filter((rb) => {
    const matchMod = selectedModule === 'ALL' || rb.affected_module === selectedModule;
    const matchStatus = selectedStatus === 'ALL' || rb.status === selectedStatus;
    return matchMod && matchStatus;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Header & Search Bar */}
      <div className="p-6 rounded-3xl glass-card border border-pink-200 bg-gradient-to-r from-white via-pink-50/20 to-purple-50/20 shadow-card-soft">
        <div>
          <h2 className="text-2xl font-bold font-['Outfit'] text-slate-900">
            Verified Runbook Knowledge Base
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Search verified troubleshooting fixes with hybrid semantic retrieval and explainable evidence citations (PRD §17).
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearchSubmit} className="mt-4 flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by issue keywords, incident ID (INC-052), or rule (RULE-TAX-104)..."
              className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-white shadow-2xs"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 text-xs sm:text-sm font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm active:scale-95 transition-all disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Sample search chips */}
        <div className="mt-3 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
          <span className="text-[11px] font-semibold text-slate-400">Try searching:</span>
          {sampleSearches.map((term, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSampleClick(term)}
              className="px-2.5 py-0.5 rounded-full bg-pink-100/60 hover:bg-pink-100 text-rose-700 text-[11px] font-medium border border-pink-200 transition-colors"
            >
              {term}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-500">Status:</span>
          {['ALL', 'VERIFIED', 'PENDING_APPROVAL', 'OVERRIDDEN'].map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                selectedStatus === st
                  ? 'bg-rose-500 text-white font-bold'
                  : 'bg-white text-slate-600 border border-pink-100 hover:bg-rose-50'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="text-xs text-slate-500">
          Prioritized: <span className="font-semibold text-emerald-600">VERIFIED</span> &gt; <span className="font-semibold text-amber-600">PARTIAL</span> &gt; UNVERIFIED
        </div>
      </div>

      {/* Runbook Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredRunbooks.map((rb) => (
          <div
            key={rb.runbook_id}
            onClick={() => onSelectRunbook(rb)}
            className="p-5 rounded-3xl glass-card border border-pink-200 hover:border-rose-300 transition-all duration-200 cursor-pointer shadow-card-soft hover:shadow-md flex flex-col justify-between"
          >
            <div>
              {/* Header tags */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5">
                  <span className="font-mono font-bold text-xs px-2 py-0.5 rounded-md bg-rose-100 text-rose-800">
                    {rb.runbook_id}
                  </span>
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 border border-purple-100">
                    {rb.affected_module}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <RiskBadge level={rb.risk_level} showLabel={false} />
                  <EvidenceBadge status={rb.evidence_completeness} />
                </div>
              </div>

              <h3 className="text-sm sm:text-base font-bold text-slate-900 line-clamp-2 mt-1">
                {rb.title}
              </h3>
              <p className="text-xs text-slate-600 mt-1 line-clamp-2">{rb.issue}</p>

              {/* Rules */}
              {rb.business_rules && rb.business_rules.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {rb.business_rules.map((rule, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold"
                    >
                      {rule}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Footer card actions */}
            <div className="mt-4 pt-3 border-t border-pink-100 flex items-center justify-between text-xs">
              <span className="text-[11px] text-slate-400 font-mono">
                Status: <strong className="text-slate-700">{rb.status}</strong>
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => handleCopy(e, rb)}
                  className="px-2.5 py-1 rounded-lg bg-pink-50 hover:bg-pink-100 text-rose-700 font-medium flex items-center gap-1"
                >
                  {copiedId === rb.runbook_id ? (
                    <Check className="w-3 h-3 text-emerald-500" />
                  ) : (
                    <Copy className="w-3 h-3" />
                  )}
                  <span>{copiedId === rb.runbook_id ? 'Copied' : 'Copy'}</span>
                </button>

                <button
                  onClick={() => onSelectRunbook(rb)}
                  className="px-3 py-1 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold flex items-center gap-1"
                >
                  <span>Read</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
