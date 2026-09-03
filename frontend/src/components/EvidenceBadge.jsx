import React from 'react';
import { CheckCircle2, AlertCircle, HelpCircle, XCircle } from 'lucide-react';

export default function EvidenceBadge({ status, size = 'sm' }) {
  const norm = (status || 'PARTIAL').toUpperCase();

  const configs = {
    VERIFIED: {
      label: 'Verified Evidence',
      icon: CheckCircle2,
      style: 'bg-emerald-50 text-emerald-700 border-emerald-200/80 shadow-sm shadow-emerald-100',
    },
    PARTIAL: {
      label: 'Partial Evidence',
      icon: HelpCircle,
      style: 'bg-amber-50 text-amber-700 border-amber-200/80 shadow-sm shadow-amber-100',
    },
    MISSING: {
      label: 'Missing Evidence',
      icon: XCircle,
      style: 'bg-rose-50 text-rose-700 border-rose-200/80 shadow-sm shadow-rose-100',
    },
    CONFLICTING: {
      label: 'Conflicting Rules',
      icon: AlertCircle,
      style: 'bg-purple-50 text-purple-700 border-purple-200/80 shadow-sm shadow-purple-100 animate-pulse',
    },
  };

  const config = configs[norm] || configs.PARTIAL;
  const Icon = config.icon;
  const isSm = size === 'sm';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${config.style} ${
        isSm ? 'text-[11px] px-2.5 py-0.5' : 'text-xs px-3 py-1'
      }`}
    >
      <Icon className={isSm ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </span>
  );
}
