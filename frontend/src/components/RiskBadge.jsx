import React from 'react';
import { AlertTriangle, ShieldCheck, AlertOctagon } from 'lucide-react';

export default function RiskBadge({ level = 'MEDIUM', showLabel = true }) {
  const norm = (level || 'MEDIUM').toUpperCase();

  const configs = {
    HIGH: {
      label: 'High Risk (Approval Req)',
      short: 'HIGH',
      icon: AlertOctagon,
      style: 'bg-rose-100 text-rose-800 border-rose-300 shadow-sm shadow-rose-200/50',
      dot: 'bg-rose-500 animate-ping',
    },
    MEDIUM: {
      label: 'Medium Risk',
      short: 'MED',
      icon: AlertTriangle,
      style: 'bg-amber-100 text-amber-800 border-amber-300',
      dot: 'bg-amber-500',
    },
    LOW: {
      label: 'Low Risk',
      short: 'LOW',
      icon: ShieldCheck,
      style: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      dot: 'bg-emerald-500',
    },
  };

  const config = configs[norm] || configs.MEDIUM;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${config.style}`}
    >
      <span className="relative flex h-2 w-2">
        <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${config.dot}`}></span>
        <span className={`relative inline-flex rounded-full h-2 w-2 ${config.dot.split(' ')[0]}`}></span>
      </span>
      <span>{showLabel ? config.label : config.short}</span>
    </span>
  );
}
