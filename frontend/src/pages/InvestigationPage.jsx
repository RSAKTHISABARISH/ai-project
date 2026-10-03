import React, { useState, useEffect } from 'react';
import { 
  Search, 
  GitPullRequest, 
  AlertCircle, 
  CheckCircle2, 
  FileCode, 
  ShieldCheck, 
  Layers, 
  Clock,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import DiffViewer from '../components/DiffViewer';
import EvidenceBadge from '../components/EvidenceBadge';
import RiskBadge from '../components/RiskBadge';
import TimelineView from '../components/TimelineView';

export default function InvestigationPage({ onShowToast, onNavigateToAi }) {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncId, setSelectedIncId] = useState('INC-052');
  const [incident, setIncident] = useState(null);
  const [pr, setPr] = useState(null);
  const [diff, setDiff] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [rules, setRules] = useState([]);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadIncidentsList();
  }, []);

  useEffect(() => {
    if (selectedIncId) {
      loadInvestigationDetails(selectedIncId);
    }
  }, [selectedIncId]);

  const loadIncidentsList = async () => {
    try {
      const data = await api.getIncidents(50);
      setIncidents(data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadInvestigationDetails = async (incId) => {
    try {
      setLoading(true);
      const inc = await api.getIncident(incId);
      setIncident(inc);

      // Find matching PR
      const allPrs = await api.getPullRequests(50);
      const matchedPr = allPrs.find(p => p.incident_id === incId) || allPrs[0];
      setPr(matchedPr);

      if (matchedPr) {
        // Fetch diff and reviews
        const [diffData, reviewsData] = await Promise.all([
          api.getDiffByPr(matchedPr.pr_id).catch(() => null),
          api.getReviewsByPr(matchedPr.pr_id).catch(() => []),
        ]);
        setDiff(diffData);
        setReviews(reviewsData || []);
      }

      // Fetch coupled rules
      const allRules = await api.getBusinessRules();
      const relevant = allRules.filter(r => r.module === inc.affected_module);
      setRules(relevant.length > 0 ? relevant : allRules.slice(0, 2));

      // Fetch timeline events for this incident/PR
      const allEvents = await api.getEvents(50);
      const filteredEvents = allEvents.filter(
        e => e.entity_id === incId || (matchedPr && e.entity_id === matchedPr.pr_id)
      );
      setTimelineEvents(filteredEvents);

    } catch (err) {
      onShowToast({ type: 'error', title: 'Error Loading Investigation', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Top Controls: Selector and Generate Trigger */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl glass-card border border-pink-100">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <label className="text-xs font-bold text-slate-600 uppercase tracking-wider whitespace-nowrap">
            Investigate Incident:
          </label>
          <select
            value={selectedIncId}
            onChange={(e) => setSelectedIncId(e.target.value)}
            className="text-xs font-semibold px-3 py-2 rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-white shadow-2xs max-w-xs"
          >
            {incidents.map((inc) => (
              <option key={inc.incident_id} value={inc.incident_id}>
                {inc.incident_id} — {inc.title.slice(0, 45)}... ({inc.affected_module})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => onNavigateToAi(selectedIncId, pr?.pr_id)}
          className="px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 rounded-xl shadow-sm flex items-center gap-2 active:scale-95 transition-all"
        >
          <Sparkles className="w-4 h-4" />
          <span>Synthesize AI Runbook for this Fix</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {incident && (
        <div className="space-y-6">
          
          {/* Incident & PR Header Card */}
          <div className="p-6 rounded-3xl glass-card border border-pink-200 bg-gradient-to-br from-white to-pink-50/20 shadow-card-soft">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-pink-100">
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full font-mono font-bold text-xs bg-rose-100 text-rose-800 border border-rose-200">
                  {incident.incident_id}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
                  Module: {incident.affected_module}
                </span>
                <RiskBadge level={incident.severity === 'HIGH' ? 'HIGH' : 'MEDIUM'} />
              </div>

              <EvidenceBadge status={reviews.some(r => r.decision === 'APPROVED') ? 'VERIFIED' : 'PARTIAL'} />
            </div>

            <div className="mt-4">
              <h2 className="text-xl font-bold font-['Outfit'] text-slate-900">{incident.title}</h2>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">{incident.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-4 border-t border-pink-100/60 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Observed Symptoms
                </span>
                <p className="text-slate-800">{incident.symptoms}</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Team Resolution
                </span>
                <p className="text-slate-800">{incident.resolution || 'Pending verification'}</p>
              </div>
            </div>
          </div>

          {/* Dual Column: Pull Request & Code Diff vs Business Rules & Reviews */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Left Column: Code Diff & PR Artifact (7 Cols) */}
            <div className="lg:col-span-7 space-y-4">
              {pr && (
                <div className="p-4 rounded-2xl glass-card border border-pink-100">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <GitPullRequest className="w-4 h-4 text-rose-500" />
                      <span className="font-mono font-bold text-xs text-slate-800">{pr.pr_id}</span>
                      <span className="text-xs text-slate-500">• {pr.title}</span>
                    </div>
                    <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {pr.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mb-2">{pr.description}</p>
                  <div className="text-[11px] text-slate-400">Author: {pr.author}</div>
                </div>
              )}

              {diff ? (
                <div>
                  <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <FileCode className="w-4 h-4 text-rose-500" />
                    Unified Code Diff Artifact ({diff.diff_id})
                  </h4>
                  <DiffViewer
                    diffText={diff.diff_text}
                    filesChanged={diff.files_changed}
                    commitId={diff.commit_id}
                  />
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-400 glass-card rounded-2xl">
                  No diff record associated with this pull request.
                </div>
              )}
            </div>

            {/* Right Column: Coupled Business Rules, Reviewer Sign-Off & Event Timeline (5 Cols) */}
            <div className="lg:col-span-5 space-y-4">
              
              {/* Tightly Coupled Business Rules */}
              <div className="p-5 rounded-2xl glass-card border border-pink-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-purple-600" />
                  Coupled ERP Business Rules
                </h4>
                <div className="space-y-3">
                  {rules.map((rule) => (
                    <div key={rule.rule_code} className="p-3 rounded-xl bg-purple-50/50 border border-purple-100 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-purple-800">{rule.rule_code}</span>
                        <RiskBadge level={rule.severity} showLabel={false} />
                      </div>
                      <h5 className="font-semibold text-slate-800 mt-1">{rule.title}</h5>
                      <p className="text-[11px] text-slate-600 mt-1">{rule.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reviewer Resolution */}
              <div className="p-5 rounded-2xl glass-card border border-pink-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Reviewer Sign-Off & Approvals
                </h4>
                {reviews.length > 0 ? (
                  <div className="space-y-2">
                    {reviews.map((rev) => (
                      <div key={rev.review_id} className="p-3 rounded-xl bg-emerald-50/40 border border-emerald-100 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-800">{rev.reviewer}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            {rev.decision}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-700 mt-1 italic">"{rev.comments}"</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No reviewer record found.</p>
                )}
              </div>

              {/* Chronological Event Timeline */}
              <div className="p-5 rounded-2xl glass-card border border-pink-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-rose-500" />
                  Incident Event Timeline
                </h4>
                <TimelineView events={timelineEvents} />
              </div>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}
