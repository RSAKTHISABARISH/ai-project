import React from 'react';
import { Clock, GitPullRequest, AlertCircle, CheckCircle, ArrowRight, Shield } from 'lucide-react';

export default function TimelineView({ events = [] }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 text-xs">
        No timeline events recorded yet.
      </div>
    );
  }

  const getEventIcon = (type) => {
    switch (type) {
      case 'INCIDENT_CREATED':
      case 'INCIDENT_RESOLVED':
        return AlertCircle;
      case 'PR_CREATED':
      case 'PR_APPROVED':
        return GitPullRequest;
      case 'REVIEW_APPROVED':
        return CheckCircle;
      default:
        return Clock;
    }
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-rose-400 before:via-pink-300 before:to-purple-400">
      {events.map((evt, idx) => {
        const Icon = getEventIcon(evt.event_type);
        const isReconciled = evt.status === 'RECONCILED';
        const isDuplicate = evt.status === 'DUPLICATE' || evt.action_taken === 'IGNORED_DUPLICATE';
        const isOOO = evt.status === 'QUEUED_OUT_OF_ORDER';

        return (
          <div key={evt.event_id || idx} className="relative group">
            {/* Timeline Dot */}
            <div className="absolute -left-6 top-1.5 w-4 h-4 rounded-full bg-white border-2 border-rose-500 flex items-center justify-center shadow-sm group-hover:scale-125 transition-transform">
              <div className="w-1.5 h-1.5 rounded-full bg-rose-500"></div>
            </div>

            <div className="bg-white/80 backdrop-blur-sm border border-pink-100 rounded-xl p-3 shadow-xs hover:border-pink-300 transition-colors">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-800 font-mono">
                    {evt.event_type}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono">
                    {evt.entity_id}
                  </span>
                  {isDuplicate && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">
                      DUPLICATE FILTERED
                    </span>
                  )}
                  {isOOO && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 font-semibold animate-pulse">
                      OUT-OF-ORDER QUEUED
                    </span>
                  )}
                  {isReconciled && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                      RECONCILED
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>
                    {evt.event_timestamp ? new Date(evt.event_timestamp).toLocaleTimeString() : 'Just now'}
                  </span>
                </div>
              </div>

              {evt.payload && Object.keys(evt.payload).length > 0 && (
                <div className="mt-1.5 text-[11px] text-slate-600 font-mono bg-pink-50/40 p-1.5 rounded border border-pink-100/60">
                  {JSON.stringify(evt.payload)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
