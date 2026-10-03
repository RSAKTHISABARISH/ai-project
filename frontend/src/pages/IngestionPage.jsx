import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Copy, 
  Clock, 
  Shuffle, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  Send,
  RefreshCw,
  Layers,
  History
} from 'lucide-react';
import { api } from '../api/client';

export default function IngestionPage({ onShowToast }) {
  const [events, setEvents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [customJson, setCustomJson] = useState(`{
  "event_id": "EVT-CUSTOM-001",
  "event_type": "PR_CREATED",
  "source": "github",
  "entity_id": "PR-999",
  "event_timestamp": "${new Date().toISOString()}",
  "payload": { "title": "Custom Ingested PR" },
  "version": 1
}`);

  const loadEventData = async () => {
    try {
      setLoading(true);
      const [evts, auditLogs] = await Promise.all([
        api.getEvents(30),
        api.getEventLogs(30),
      ]);
      setEvents(evts || []);
      setLogs(auditLogs || []);
    } catch (err) {
      onShowToast({ type: 'error', title: 'Error Loading Events', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEventData();
  }, []);

  const handleInjectDuplicate = async () => {
    try {
      setLoading(true);
      const res = await api.injectDuplicate();
      onShowToast({
        type: 'info',
        title: 'Edge Case 1: Duplicate Event Filtered',
        message: `${res.message} Second attempt status: ${res.second_attempt_duplicate_check.action}`,
      });
      await loadEventData();
    } catch (err) {
      onShowToast({ type: 'error', title: 'Duplicate Test Failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleInjectDelayed = async () => {
    try {
      setLoading(true);
      const res = await api.injectDelayed();
      onShowToast({
        type: 'success',
        title: 'Edge Case 2: Delayed Event Ingested',
        message: `Reconstructed into logical timeline at ${new Date(res.logical_timestamp).toLocaleTimeString()}`,
      });
      await loadEventData();
    } catch (err) {
      onShowToast({ type: 'error', title: 'Delayed Test Failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleInjectOutOfOrder = async () => {
    try {
      setLoading(true);
      const res = await api.injectOutOfOrder();
      onShowToast({
        type: 'success',
        title: 'Edge Case 3: Out-of-Order Handled & Reconciled',
        message: `Step 1: ${res.step_1_out_of_order_review.action} -> Step 2: ${res.step_2_pr_arrived_and_reconciled.action}`,
      });
      await loadEventData();
    } catch (err) {
      onShowToast({ type: 'error', title: 'Out of Order Test Failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleCustomIngest = async () => {
    try {
      setLoading(true);
      const parsed = JSON.parse(customJson);
      const res = await api.ingestEvent(parsed);
      onShowToast({
        type: 'success',
        title: 'Event Ingested',
        message: `${res.message} Status: ${res.action}`,
      });
      await loadEventData();
    } catch (err) {
      onShowToast({ type: 'error', title: 'Ingestion Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-['Outfit'] text-slate-900">
          Data Ingestion & Event Processing Lab
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Test event-driven idempotency, delayed arrival timeline reconstruction, and out-of-order state machine reconciliation (PRD §8, §9, §10, §18).
        </p>
      </div>

      {/* Interactive Edge Case Injection Action Cards (PRD §18 & §27) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Edge Case 1: Duplicate Event */}
        <div className="p-5 rounded-2xl glass-card border border-pink-200 hover:border-pink-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-pink-100 text-rose-600 flex items-center justify-center mb-3">
            <Copy className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">Edge Case 1: Duplicate Event</h3>
          <p className="text-xs text-slate-500 mt-1">
            Sends the exact same PR_APPROVED event twice. Proves the idempotency engine skips duplicate processing and preserves final state.
          </p>
          <button
            onClick={handleInjectDuplicate}
            disabled={loading}
            className="mt-4 w-full py-2 px-3 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-xl transition-colors active:scale-95 disabled:opacity-50"
          >
            Inject Duplicate Event
          </button>
        </div>

        {/* Edge Case 2: Delayed Event */}
        <div className="p-5 rounded-2xl glass-card border border-purple-200 hover:border-purple-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-3">
            <Clock className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">Edge Case 2: Delayed Event</h3>
          <p className="text-xs text-slate-500 mt-1">
            Sends an incident resolution event with an older timestamp arriving late. Reconstructs logical sequence using event_timestamp.
          </p>
          <button
            onClick={handleInjectDelayed}
            disabled={loading}
            className="mt-4 w-full py-2 px-3 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-xl transition-colors active:scale-95 disabled:opacity-50"
          >
            Inject Delayed Event
          </button>
        </div>

        {/* Edge Case 3: Out-of-Order Events */}
        <div className="p-5 rounded-2xl glass-card border border-emerald-200 hover:border-emerald-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3">
            <Shuffle className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">Edge Case 3: Out-of-Order</h3>
          <p className="text-xs text-slate-500 mt-1">
            Injects Reviewer Approval BEFORE PR creation. The state machine queues it and automatically reconciles when PR arrives.
          </p>
          <button
            onClick={handleInjectOutOfOrder}
            disabled={loading}
            className="mt-4 w-full py-2 px-3 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition-colors active:scale-95 disabled:opacity-50"
          >
            Inject Out-of-Order Sequence
          </button>
        </div>

      </div>

      {/* Manual JSON Ingestion Editor */}
      <div className="glass-card rounded-2xl border border-pink-100 p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <UploadCloud className="w-4 h-4 text-rose-500" />
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Manual JSON Event Ingestion
            </h4>
          </div>
          <button
            onClick={handleCustomIngest}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs flex items-center gap-1.5 shadow-sm active:scale-95 disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Ingest Event</span>
          </button>
        </div>
        <textarea
          rows={6}
          value={customJson}
          onChange={(e) => setCustomJson(e.target.value)}
          className="w-full text-xs font-mono p-3 rounded-xl border border-pink-200 focus:outline-none focus:ring-2 focus:ring-rose-400 bg-slate-950 text-slate-100"
        />
      </div>

      {/* Live Event Stream & Processing Log Tabs */}
      <div className="glass-card rounded-2xl border border-pink-100 overflow-hidden">
        <div className="p-4 border-b border-pink-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-rose-500" />
            <h3 className="text-sm font-bold text-slate-800">
              Live Ingested Event Log ({events.length} events)
            </h3>
          </div>
          <button
            onClick={loadEventData}
            disabled={loading}
            className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            title="Refresh logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left text-xs">
            <thead className="bg-pink-50/50 text-slate-500 font-semibold border-b border-pink-100 sticky top-0">
              <tr>
                <th className="p-3 pl-5">Event ID</th>
                <th className="p-3">Event Type</th>
                <th className="p-3">Entity ID</th>
                <th className="p-3">Event Timestamp</th>
                <th className="p-3">Processing State</th>
                <th className="p-3 pr-5">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pink-50">
              {events.map((evt) => {
                let badgeStyle = 'bg-slate-100 text-slate-700';
                if (evt.status === 'PROCESSED') badgeStyle = 'bg-emerald-50 text-emerald-700 border border-emerald-200';
                if (evt.status === 'IGNORED_DUPLICATE' || evt.status === 'DUPLICATE') badgeStyle = 'bg-amber-50 text-amber-700 border border-amber-200';
                if (evt.status === 'QUEUED_OUT_OF_ORDER') badgeStyle = 'bg-purple-50 text-purple-700 border border-purple-200 animate-pulse';
                if (evt.status === 'RECONCILED') badgeStyle = 'bg-teal-50 text-teal-700 border border-teal-200';

                return (
                  <tr key={evt.event_id} className="hover:bg-rose-50/30 transition-colors">
                    <td className="p-3 pl-5 font-mono font-bold text-slate-800">{evt.event_id}</td>
                    <td className="p-3 font-semibold text-slate-900">{evt.event_type}</td>
                    <td className="p-3 font-mono text-slate-600">{evt.entity_id}</td>
                    <td className="p-3 text-slate-500">
                      {evt.event_timestamp ? new Date(evt.event_timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="p-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${badgeStyle}`}>
                        {evt.status}
                      </span>
                    </td>
                    <td className="p-3 pr-5 text-slate-400 capitalize">{evt.source}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
