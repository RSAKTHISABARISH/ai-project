import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'rose', trend }) {
  const colorStyles = {
    rose: {
      bg: 'bg-rose-50/70',
      border: 'border-rose-200/80',
      iconBg: 'bg-rose-500 text-white',
      trendColor: 'text-rose-600',
    },
    pink: {
      bg: 'bg-pink-50/70',
      border: 'border-pink-200/80',
      iconBg: 'bg-pink-500 text-white',
      trendColor: 'text-pink-600',
    },
    purple: {
      bg: 'bg-purple-50/70',
      border: 'border-purple-200/80',
      iconBg: 'bg-purple-600 text-white',
      trendColor: 'text-purple-600',
    },
    emerald: {
      bg: 'bg-emerald-50/70',
      border: 'border-emerald-200/80',
      iconBg: 'bg-emerald-500 text-white',
      trendColor: 'text-emerald-600',
    },
    amber: {
      bg: 'bg-amber-50/70',
      border: 'border-amber-200/80',
      iconBg: 'bg-amber-500 text-white',
      trendColor: 'text-amber-600',
    },
  };

  const style = colorStyles[color] || colorStyles.rose;

  return (
    <div className={`p-5 rounded-2xl glass-card border ${style.border} relative overflow-hidden transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl sm:text-3xl font-bold font-['Outfit'] text-slate-900 mt-1">{value}</h3>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
              {trend && <span className={`font-semibold ${style.trendColor}`}>{trend}</span>}
              <span>{subtitle}</span>
            </p>
          )}
        </div>
        {Icon && (
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-sm ${style.iconBg}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${style.border.replace('border-', 'from-')} to-transparent`} />
    </div>
  );
}
