import React from 'react';
import { GitCommit, FileCode, Check, Copy } from 'lucide-react';

export default function DiffViewer({ diffText, filesChanged = [], commitId }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    if (!diffText) return;
    navigator.clipboard.writeText(diffText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = (diffText || '').split('\n');

  return (
    <div className="rounded-xl border border-pink-200/80 bg-slate-950 text-slate-100 overflow-hidden font-mono text-xs shadow-inner">
      {/* Diff Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-2 text-slate-300">
          <FileCode className="w-4 h-4 text-rose-400" />
          <span className="font-semibold text-slate-200">
            {filesChanged.length > 0 ? filesChanged.join(', ') : 'Code Changes'}
          </span>
          {commitId && (
            <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-purple-300 flex items-center gap-1">
              <GitCommit className="w-3 h-3" />
              {commitId}
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 px-2 py-1 rounded transition-colors"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied' : 'Copy Diff'}</span>
        </button>
      </div>

      {/* Diff Lines */}
      <div className="p-3 overflow-x-auto max-h-80 select-text leading-relaxed">
        {lines.map((line, idx) => {
          let lineStyle = 'text-slate-400';
          let bgStyle = '';

          if (line.startsWith('+') && !line.startsWith('+++')) {
            lineStyle = 'text-emerald-300 font-semibold';
            bgStyle = 'bg-emerald-950/40 border-l-2 border-emerald-500 pl-1';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            lineStyle = 'text-rose-300';
            bgStyle = 'bg-rose-950/40 border-l-2 border-rose-500 pl-1';
          } else if (line.startsWith('@@')) {
            lineStyle = 'text-purple-300 font-semibold';
            bgStyle = 'bg-purple-950/30';
          }

          return (
            <div key={idx} className={`py-0.5 whitespace-pre ${lineStyle} ${bgStyle}`}>
              {line || ' '}
            </div>
          );
        })}
      </div>
    </div>
  );
}
