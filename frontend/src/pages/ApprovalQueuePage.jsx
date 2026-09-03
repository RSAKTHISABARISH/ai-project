import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  AlertOctagon, 
  Edit3, 
  History, 
  Layers, 
  Check, 
  User,
  Clock,
  FileText
} from 'lucide-react';
import { api } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import EvidenceBadge from '../components/EvidenceBadge';

export default function ApprovalQueuePage({ onOpenApproval, onShowToast }) {
  const [pendingRunbooks, setPendingRunbooks] = useState([]);
  const [allRunbooks, setAllRunbooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAuditHistory, setSelectedAuditHistory] = useState([]);
  const [auditTargetId, setAuditTargetId] = useState(null);

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getRunbooks();
      const all = data || [];
      setAllRunbooks(all);
      setPendingRunbooks(all.filter(r => r.status === 'PENDING_APPROVAL'));
    } catch (err) {
      onShowToast({ type: 'error', title: 'Error Loading Approvals', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleViewAuditHistory = async (rbId) => {
    try {
      const history = await api.getOverrideHistory(rbId);
      setSelectedAuditHistory(history || []);
      setAuditTargetId(rbId);
    } catch (err) {
      onShowToast({ type: 'error', title: 'Error Fetching Audit History', message: err.message });
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-['Outfit'] text-slate-900">
          High-Impact Human Approval & Override Governance
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Strict safety guardrail: High-risk actions modifying financial calculations, tax rates, payments, or access controls cannot execute automatically (PRD §14).
        </p>
      </div>

      {/* Pending High-Impact Recommendations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <h3 className="text-base font-bold text-slate-800">
              Pending Human Sign-Off Queue ({pendingRunbooks.length})
            </h3>
          </div>
          <span className="text-xs text-slate-400">
            Mandatory audit tracking enforced for all decisions
          </span>
        </div>

        {pendingRunbooks.length === 0 ? (
          <div className="p-8 rounded-3xl glass-card border border-pink-100 text-center text-slate-500 text-xs">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="font-semibold text-slate-700">All high-impact actions have been reviewed.</p>
            <p className="text-slate-400 mt-0.5">Generate a new runbook for a financial or tax incident to test human approval.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {pendingRunbooks.map((rb) => (
              <div
                key={rb.runbook_id}
                className="p-6 rounded-3xl glass-card border border-rose-200 bg-gradient-to-r from-white via-rose-50/20 to-purple-50/20 shadow-card-soft space-y-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
                      {rb.runbook_id}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                      Module: {rb.affected_module}
                    </span>
                    <RiskBadge level={rb.risk_level} />
                    <EvidenceBadge status={rb.evidence_completeness} />
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onOpenApproval(rb)}
                      className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm flex items-center gap-1.5 active:scale-95 transition-all"
                    >
                      <ShieldAlert className="w-4 h-4" />
                      <span>Review, Approve or Override</span>
                    </button>
                  </div>
                </div>

                <div>
                  <h4 className="text-base font-bold text-slate-900">{rb.title}</h4>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{rb.issue}</p>
                </div>

                <div className="p-3 rounded-2xl bg-rose-50 border border-rose-100 text-xs text-rose-800">
                  <strong className="font-bold">Risk Reason:</strong> Modifies financial or calculation logic in{' '}
                  <span className="font-mono font-semibold">{rb.affected_module}</span> ({rb.business_rules?.join(', ')}).
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Governed Runbooks & Audit History Table */}
      <div className="glass-card rounded-3xl border border-pink-100 overflow-hidden">
        <div className="p-5 border-b border-pink-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold font-['Outfit'] text-slate-800 flex items-center gap-2">
              <History className="w-4 h-4 text-purple-600" />
              All Runbooks Governance & Approval Status
            </h3>
            <p className="text-xs text-slate-500">
              Audit log of approved, rejected, and overridden knowledge items.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-pink-50/40 text-slate-500 font-semibold border-b border-pink-100">
              <tr>
                <th className="p-3.5 pl-5">Runbook ID</th>
                <th className="p-3.5">Title</th>
                <th className="p-3.5">Module</th>
                <th className="p-3.5">Risk</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 pr-5 text-right">Audit History</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pink-50">
              {allRunbooks.map((rb) => (
                <tr key={rb.runbook_id} className="hover:bg-rose-50/30 transition-colors">
                  <td className="p-3.5 pl-5 font-mono font-bold text-slate-800">{rb.runbook_id}</td>
                  <td className="p-3.5 font-medium text-slate-900 max-w-sm truncate">{rb.title}</td>
                  <td className="p-3.5 font-semibold text-purple-700">{rb.affected_module}</td>
                  <td className="p-3.5">
                    <RiskBadge level={rb.risk_level} showLabel={false} />
                  </td>
                  <td className="p-3.5">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold font-mono ${
                      rb.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' :
                      rb.status === 'OVERRIDDEN' ? 'bg-purple-100 text-purple-800' :
                      rb.status === 'REJECTED' ? 'bg-rose-100 text-rose-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {rb.status}
                    </span>
                  </td>
                  <td className="p-3.5 pr-5 text-right">
                    <button
                      onClick={() => handleViewAuditHistory(rb.runbook_id)}
                      className="px-2.5 py-1 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg transition-colors"
                    >
                      Audit Trail
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Audit Trail Modal / Inspector */}
      {auditTargetId && (
        <div className="p-5 rounded-3xl glass-card border border-purple-200 bg-purple-50/30 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-4 h-4 text-purple-600" />
              Override & Approval Audit Log for {auditTargetId}
            </h4>
            <button
              onClick={() => setAuditTargetId(null)}
              className="text-xs text-purple-700 font-semibold hover:underline"
            >
              Close Log
            </button>
          </div>

          {selectedAuditHistory.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No manual overrides recorded for this item.</p>
          ) : (
            <div className="space-y-2">
              {selectedAuditHistory.map((entry) => (
                <div key={entry.id} className="p-3 rounded-xl bg-white border border-purple-100 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800 flex items-center gap-1">
                      <User className="w-3 h-3 text-purple-600" />
                      {entry.user}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-1">
                    <strong className="text-purple-800">Decision:</strong> {entry.final_decision}
                  </div>
                  <div className="mt-0.5 text-slate-700">
                    <strong className="text-slate-500">Reason:</strong> {entry.reason}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

    </div>
  );
}
