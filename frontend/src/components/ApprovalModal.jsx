import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle, AlertOctagon, Edit3, Lock } from 'lucide-react';
import RiskBadge from './RiskBadge';
import EvidenceBadge from './EvidenceBadge';

export default function ApprovalModal({ isOpen, onClose, runbook, onApprove, onReject, onOverride, loading }) {
  if (!isOpen || !runbook) return null;

  const [activeAction, setActiveAction] = useState('approve'); // 'approve', 'reject', 'override'
  const [decidedBy, setDecidedBy] = useState('Senior ERP Engineer');
  const [reason, setReason] = useState('');
  const [overrideProcedure, setOverrideProcedure] = useState(
    runbook.fix_procedure ? runbook.fix_procedure.join('\n') : ''
  );
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');

    if ((activeAction === 'reject' || activeAction === 'override') && !reason.trim()) {
      setErrorMsg('Mandatory reason is strictly required for rejection or override (PRD §14).');
      return;
    }

    if (activeAction === 'approve') {
      onApprove(runbook.runbook_id, {
        decided_by: decidedBy,
        reason: reason || 'Human verified calculation & safety boundaries.',
        potential_impact: `Production deployment approved for module ${runbook.affected_module}.`,
      });
    } else if (activeAction === 'reject') {
      onReject(runbook.runbook_id, {
        decided_by: decidedBy,
        reason: reason.trim(),
        potential_impact: 'Action rejected by engineering reviewer.',
      });
    } else if (activeAction === 'override') {
      const procArray = overrideProcedure
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean);
      onOverride(runbook.runbook_id, {
        user: decidedBy,
        reason: reason.trim(),
        modified_procedure: procArray,
        final_decision: 'OVERRIDDEN',
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-pink-200 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header Banner */}
        <div className="bg-gradient-to-r from-rose-500 via-pink-600 to-purple-600 p-6 text-white relative rounded-t-3xl">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white p-1 rounded-full hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-white/20 text-white text-xs font-semibold backdrop-blur-sm">
              HIGH-IMPACT GOVERNANCE
            </span>
            <span className="text-xs text-rose-100 font-mono">{runbook.runbook_id}</span>
          </div>
          <h2 className="text-xl font-bold font-['Outfit'] mt-1">{runbook.title}</h2>
          <p className="text-xs text-rose-100 mt-1">
            Module: {runbook.affected_module} • Rules: {runbook.business_rules?.join(', ')}
          </p>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Risk & Safety Warning Alert */}
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-800">
                  Risk Level: HIGH • Human Approval Required
                </h4>
              </div>
              <p className="text-xs text-rose-700 mt-1">
                This runbook alters sensitive financial, calculation, or security business rules. Automated execution is blocked. An authorized engineer must confirm, reject, or override with explicit audit reasoning.
              </p>
            </div>
          </div>

          {/* Action Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-2">Select Decision</label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setActiveAction('approve')}
                className={`py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  activeAction === 'approve'
                    ? 'bg-emerald-500 text-white border-emerald-600 shadow-sm'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                <CheckCircle className="w-4 h-4" />
                <span>Approve</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAction('reject')}
                className={`py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  activeAction === 'reject'
                    ? 'bg-rose-600 text-white border-rose-700 shadow-sm'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                <AlertOctagon className="w-4 h-4" />
                <span>Reject</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAction('override')}
                className={`py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  activeAction === 'override'
                    ? 'bg-purple-600 text-white border-purple-700 shadow-sm'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                <Edit3 className="w-4 h-4" />
                <span>Modify / Override</span>
              </button>
            </div>
          </div>

          {/* Signer Identity */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Authorizing Engineer Name / Title
            </label>
            <input
              type="text"
              value={decidedBy}
              onChange={(e) => setDecidedBy(e.target.value)}
              required
              className="w-full text-xs px-3 py-2 rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-white"
            />
          </div>

          {/* Reason (Mandatory for Reject / Override) */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
              <span>
                {activeAction === 'approve' ? 'Verification Notes (Optional)' : 'Mandatory Override/Rejection Reason *'}
              </span>
              {activeAction !== 'approve' && (
                <span className="text-[10px] text-rose-600 font-bold uppercase">Required</span>
              )}
            </label>
            <textarea
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder={
                activeAction === 'approve'
                  ? 'e.g. Verified calculation logic and test matrix assertions...'
                  : 'State the precise architectural or safety rationale for overriding this fix...'
              }
              className="w-full text-xs p-3 rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-white"
            />
          </div>

          {/* Override Procedure Modification Field */}
          {activeAction === 'override' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Modified Fix Procedure (One step per line)
              </label>
              <textarea
                rows={4}
                value={overrideProcedure}
                onChange={(e) => setOverrideProcedure(e.target.value)}
                className="w-full text-xs p-3 font-mono rounded-xl border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400 bg-purple-50/20"
              />
            </div>
          )}

          {errorMsg && (
            <div className="p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-xl">
              {errorMsg}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`px-5 py-2 text-xs font-semibold text-white rounded-xl shadow-sm transition-all active:scale-95 disabled:opacity-50 ${
                activeAction === 'approve'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : activeAction === 'reject'
                  ? 'bg-rose-600 hover:bg-rose-700'
                  : 'bg-purple-600 hover:bg-purple-700'
              }`}
            >
              {loading ? 'Processing...' : `Confirm ${activeAction.toUpperCase()}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
