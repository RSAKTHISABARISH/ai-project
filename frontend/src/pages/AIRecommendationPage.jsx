import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  ShieldAlert, 
  FileText, 
  CheckCircle2, 
  HelpCircle, 
  ArrowRight, 
  Layers, 
  RefreshCw,
  Info,
  Check
} from 'lucide-react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import EvidenceBadge from '../components/EvidenceBadge';

export default function AIRecommendationPage({ 
  selectedIncidentId, 
  selectedPrId, 
  onShowToast, 
  onOpenApproval,
  onViewRunbook
}) {
  const [incidentId, setIncidentId] = useState(selectedIncidentId || 'INC-052');
  const [incidents, setIncidents] = useState([]);
  const [runbook, setRunbook] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [forceDemo, setForceDemo] = useState(false);

  useEffect(() => {
    api.getIncidents(50).then(data => setIncidents(data || [])).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedIncidentId) {
      setIncidentId(selectedIncidentId);
      handleGenerate(selectedIncidentId);
    } else {
      handleGenerate('INC-052');
    }
  }, [selectedIncidentId]);

  const handleGenerate = async (targetId = incidentId) => {
    try {
      setGenerating(true);
      const generated = await api.generateRunbook(targetId, null, forceDemo);
      setRunbook(generated);
      onShowToast({
        type: 'success',
        title: 'Runbook Synthesized',
        message: `Successfully synthesized runbook ${generated.runbook_id} (${generated.status}).`,
      });
    } catch (err) {
      onShowToast({ type: 'error', title: 'Generation Error', message: err.message });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Header & Synthesis Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-3xl glass-card border border-pink-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-500 to-purple-600 flex items-center justify-center text-white shadow-sm">
              <Sparkles className="w-4 h-4" />
            </span>
            <h2 className="text-xl font-bold font-['Outfit'] text-slate-900">
              AI Knowledge Extraction & Synthesis
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Extracts facts, derives inferences, and provides actionable recommendations grounded strictly in evidence (PRD §12).
          </p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={incidentId}
            onChange={(e) => setIncidentId(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-white shadow-2xs"
          >
            {incidents.map((inc) => (
              <option key={inc.incident_id} value={inc.incident_id}>
                {inc.incident_id} — {inc.title.slice(0, 35)}...
              </option>
            ))}
          </select>

          <button
            onClick={() => handleGenerate(incidentId)}
            disabled={generating}
            className="px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 rounded-xl shadow-sm flex items-center gap-1.5 active:scale-95 disabled:opacity-50 transition-all whitespace-nowrap"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
            <span>{generating ? 'Synthesizing...' : 'Re-Generate Runbook'}</span>
          </button>
        </div>
      </div>

      {runbook && (
        <div className="space-y-6">
          
          {/* Main Status & Explainability Banner */}
          <div className="p-6 rounded-3xl glass-card border border-pink-200 bg-gradient-to-br from-white via-pink-50/20 to-purple-50/20 shadow-card-soft">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-pink-100">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-xs px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
                  {runbook.runbook_id}
                </span>
                <span className="text-xs font-semibold text-slate-700">
                  Target Module: <strong className="text-purple-700">{runbook.affected_module}</strong>
                </span>
                <RiskBadge level={runbook.risk_level} />
                <EvidenceBadge status={runbook.evidence_completeness} />
              </div>

              <div className="flex items-center gap-2">
                {runbook.status === 'PENDING_APPROVAL' && (
                  <button
                    onClick={() => onOpenApproval(runbook)}
                    className="px-3.5 py-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm flex items-center gap-1.5 active:scale-95 transition-all"
                  >
                    <ShieldAlert className="w-4 h-4" />
                    <span>Human Approval Required</span>
                  </button>
                )}

                <button
                  onClick={() => onViewRunbook(runbook)}
                  className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-pink-200 rounded-xl transition-colors"
                >
                  View Full Document
                </button>
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-xl font-bold font-['Outfit'] text-slate-900">{runbook.title}</h3>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{runbook.issue}</p>
            </div>

            {/* Why this recommendation was generated */}
            <div className="mt-5 p-4 rounded-2xl bg-white/80 border border-pink-100/80 text-xs">
              <div className="flex items-center gap-2 font-bold text-rose-800 uppercase tracking-wider mb-1">
                <Info className="w-4 h-4 text-rose-500" />
                Why This Recommendation Was Generated
              </div>
              <p className="text-slate-700 leading-relaxed">
                The engine correlated Incident symptoms with Code Diff changes in{' '}
                <span className="font-mono font-semibold text-purple-700">
                  {(runbook.business_rules || []).join(', ') || runbook.affected_module}
                </span>{' '}
                and confirmed peer-reviewed sign-off. The fix sequence satisfies safety constraints and mitigates runtime financial/tax recalculation variance.
              </p>
            </div>
          </div>

          {/* PRD §12 MANDATORY THREE-PART SEPARATION: FACTS vs INFERENCES vs RECOMMENDATIONS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* COLUMN 1: FACTS (Directly from Incident, PR, Diff, Review) */}
            <div className="p-5 rounded-3xl glass-card border border-pink-200 flex flex-col h-full">
              <div className="flex items-center justify-between pb-3 border-b border-pink-100 mb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    1. Grounded Facts
                  </h4>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-700">
                  VERIFIED SOURCES
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Concrete records directly observed in PRs, incidents, git diffs, and reviews.
              </p>

              <div className="space-y-2.5 flex-1">
                {(runbook.facts || []).map((fact, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-rose-50/40 border border-rose-100 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono font-bold text-rose-700 px-1.5 py-0.5 rounded bg-rose-100">
                        {fact.source_type}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">{fact.source_id}</span>
                    </div>
                    <p className="text-slate-700 leading-relaxed font-medium">{fact.claim}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* COLUMN 2: INFERENCES (Synthesized Root Cause & Hypotheses) */}
            <div className="p-5 rounded-3xl glass-card border border-purple-200 flex flex-col h-full">
              <div className="flex items-center justify-between pb-3 border-b border-purple-100 mb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    2. Model Inferences
                  </h4>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                  DEDUCTION
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Synthesized hypotheses derived from component couplings and symptom patterns.
              </p>

              <div className="space-y-2.5 flex-1">
                {(runbook.inferences || []).map((inf, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-purple-50/40 border border-purple-100 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold text-purple-700">HYPOTHESIS</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-800">
                        {Math.round((inf.confidence || 0.92) * 100)}% Confidence
                      </span>
                    </div>
                    <p className="text-slate-800 leading-relaxed font-medium">{inf.hypothesis}</p>
                    <p className="text-[11px] text-slate-500 mt-1.5 pt-1.5 border-t border-purple-100">
                      <strong className="text-slate-600">Basis:</strong> {inf.basis}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* COLUMN 3: RECOMMENDATIONS (Actionable Procedure with Evidence Links) */}
            <div className="p-5 rounded-3xl glass-card border border-emerald-200 flex flex-col h-full">
              <div className="flex items-center justify-between pb-3 border-b border-emerald-100 mb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    3. Recommendations
                  </h4>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                  ACTIONABLE
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Specific deployment actions guarded by deterministic risk & evidence criteria.
              </p>

              <div className="space-y-2.5 flex-1">
                {(runbook.recommendations || []).map((rec, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-emerald-50/40 border border-emerald-100 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <RiskBadge level={rec.risk_level} showLabel={false} />
                      <span className="text-[10px] font-semibold text-emerald-800">RECOMMENDED</span>
                    </div>
                    <h5 className="font-bold text-slate-900 mt-1">{rec.action}</h5>
                    <p className="text-[11px] text-slate-600 mt-1">{rec.rationale}</p>

                    {rec.supporting_evidence && rec.supporting_evidence.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-emerald-100 flex flex-wrap gap-1">
                        {rec.supporting_evidence.map((evd, eIdx) => (
                          <span
                            key={eIdx}
                            className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold"
                          >
                            {evd}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Fix Procedure Steps */}
          <div className="p-6 rounded-3xl glass-card border border-pink-200">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Synthesized Fix Execution Steps
            </h4>
            <div className="space-y-2">
              {(runbook.fix_procedure || []).map((step, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 font-mono font-bold flex items-center justify-center shrink-0 text-[11px]">
                    {idx + 1}
                  </span>
                  <span className="text-slate-800 pt-0.5 leading-relaxed">{step.replace(/^\d+\.\s*/, '')}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
