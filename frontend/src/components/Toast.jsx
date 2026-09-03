import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4500);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  const typeStyles = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    error: 'bg-rose-50 border-rose-200 text-rose-800',
    info: 'bg-purple-50 border-purple-200 text-purple-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
  };

  const Icon = toast.type === 'error' ? AlertCircle : toast.type === 'info' ? Info : CheckCircle2;

  return (
    <div className="fixed bottom-5 right-5 z-50 animate-in slide-in-from-bottom-5 duration-200">
      <div
        className={`flex items-start gap-3 p-4 rounded-2xl border shadow-xl backdrop-blur-md max-w-md ${
          typeStyles[toast.type] || typeStyles.info
        }`}
      >
        <Icon className="w-5 h-5 shrink-0 mt-0.5 text-current" />
        <div className="flex-1">
          {toast.title && <h5 className="text-xs font-bold font-['Outfit']">{toast.title}</h5>}
          <p className="text-xs mt-0.5 leading-relaxed">{toast.message}</p>
        </div>
        <button onClick={onClose} className="text-current opacity-60 hover:opacity-100 p-0.5">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
