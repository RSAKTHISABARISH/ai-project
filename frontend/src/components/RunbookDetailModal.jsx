import React, { useState } from 'react';
import { X, Copy, Check, Shield, BookOpen, AlertTriangle, Layers, FileText, CheckCircle2 } from 'lucide-react';
import RiskBadge from './RiskBadge';
import EvidenceBadge from './EvidenceBadge';

export default function RunbookDetailModal({ isOpen, onClose, runbook, onOpenApproval }) {
  if (!isOpen || !runbook) return null;

  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = `
# ${runbook.title}
ID: ${runbook.runbook_id}
Module: ${runbook.affected_module}
Status: ${runbook.status}
Risk: ${runbook.risk_level}
Evidence Completeness: ${runbook.evidence_completeness}

## ISSUE
${runbook.issue}

## SYMPTOMS
${runbook.symptoms}

## ROOT CAUSE
${runbook.root_cause}

## BUSINESS RULES
${(runbook.business_rules || []).join(', ')}

## PRECONDITIONS
${(runbook.preconditions || []).join('\n')}

## FIX PROCEDURE
${(runbook.fix_procedure || []).join('\n')}

## VALIDATION
${(runbook.validation_steps || []).join('\n')}

## ROLLBACK
${(runbook.rollback_procedure || []).join('\n')}
    `.trim();

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-pink-200 max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-rose-500 via-pink-600 to-purple-600 p-6 text-white relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white p-1 rounded-full hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full bg-white/20 text-white text-xs font-mono font-bold">
              {runbook.runbook_id}
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-white/20 text-white text-xs">
              Module: {runbook.affected_module}
            </span>
            <RiskBadge level={runbook.risk_level} />
            <EvidenceBadge status={runbook.evidence_completeness} />
          </div>
          <h2 className="text-xl sm:text-2xl font-bold font-['Outfit']">{runbook.title}</h2>
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between px-6 py-3 bg-pink-50/50 border-b border-pink-100 text-xs">
          <div className="flex items-center gap-2 text-slate-600">
            <span className="font-semibold">Current State:</span>
            <span className="px-2 py-0.5 rounded-md font-mono font-bold text-rose-700 bg-rose-100/70 border border-rose-200">
              {runbook.status}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {runbook.status === 'PENDING_APPROVAL' && (
              <button
                onClick={() => {
                  onClose();
                  onOpenApproval(runbook);
                }}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold flex items-center gap-1.5 shadow-sm"
              >
                <Shield className="w-3.5 h-3.5" />
                <span>Review & Approve</span>
              </button>
            )}

            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg bg-white border border-pink-200 text-slate-700 hover:bg-pink-50 font-medium flex items-center gap-1.5 shadow-2xs"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Runbook'}</span>
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs sm:text-sm text-slate-700">
          
          {/* Issue & Symptoms Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <FileText className="w-3.5 h-3.5 text-rose-500" />
                Issue Description
              </h4>
              <p className="text-slate-800 leading-relaxed">{runbook.issue}</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                Observed Symptoms
              </h4>
              <p className="text-slate-800 leading-relaxed">{runbook.symptoms}</p>
            </div>
          </div>

          {/* Root Cause */}
          <div className="p-4 rounded-2xl bg-rose-50/50 border border-rose-100">
            <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-1">Root Cause Analysis</h4>
            <p className="text-slate-800 leading-relaxed">{runbook.root_cause}</p>
          </div>

          {/* Business Rules Involved */}
          {runbook.business_rules && runbook.business_rules.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Tightly-Coupled Business Rules
              </h4>
              <div className="flex flex-wrap gap-2">
                {runbook.business_rules.map((rule, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-purple-50 text-purple-700 font-mono text-xs font-semibold border border-purple-200"
                  >
                    {rule}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Preconditions */}
          {runbook.preconditions && runbook.preconditions.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Mandatory Preconditions
              </h4>
              <ul className="space-y-1.5 pl-2">
                {runbook.preconditions.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0"></span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Fix Procedure */}
          <div>
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              Verified Step-by-Step Fix Procedure
            </h4>
            <div className="p-4 rounded-2xl bg-emerald-50/40 border border-emerald-100 space-y-2">
              {(runbook.fix_procedure || []).map((step, idx) => (
                <div key={idx} className="flex items-start gap-2 text-slate-800">
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono font-bold text-[11px] shrink-0">
                    {idx + 1}
                  </span>
                  <span className="pt-0.5 leading-relaxed">{step.replace(/^\d+\.\s*/, '')}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Validation & Rollback */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Post-Fix Validation Steps
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {(runbook.validation_steps || []).map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-500 font-bold">✓</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 text-rose-600">
                Emergency Rollback Procedure
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {(runbook.rollback_procedure || []).map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-rose-500 font-bold">↺</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Supporting Evidence Chain */}
          {runbook.evidence_graph && (
            <div className="p-4 rounded-2xl bg-pink-50/30 border border-pink-100">
              <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-rose-500" />
                Linked Evidence Chain
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div className="p-2 rounded-xl bg-white border border-pink-100">
                  <span className="text-[10px] text-slate-400 block font-semibold">INCIDENT</span>
                  <span className="font-mono font-bold text-slate-800">
                    {runbook.evidence_graph.incident?.incident_id || 'N/A'}
                  </span>
                </div>
                <div className="p-2 rounded-xl bg-white border border-pink-100">
                  <span className="text-[10px] text-slate-400 block font-semibold">PULL REQUEST</span>
                  <span className="font-mono font-bold text-slate-800">
                    {runbook.evidence_graph.pull_request?.pr_id || 'N/A'}
                  </span>
                </div>
                <div className="p-2 rounded-xl bg-white border border-pink-100">
                  <span className="text-[10px] text-slate-400 block font-semibold">DIFF ARTIFACT</span>
                  <span className="font-mono font-bold text-slate-800">
                    {runbook.evidence_graph.code_diff?.diff_id || 'N/A'}
                  </span>
                </div>
                <div className="p-2 rounded-xl bg-white border border-pink-100">
                  <span className="text-[10px] text-slate-400 block font-semibold">REVIEWS</span>
                  <span className="font-mono font-bold text-slate-800">
                    {runbook.evidence_graph.reviews?.length || 0} Approval(s)
                  </span>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
