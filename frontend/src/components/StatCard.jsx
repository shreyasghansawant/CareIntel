import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'sky', badge }) {
  const colorMap = {
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  const badgeColorMap = {
    sky: 'bg-sky-950 text-sky-300 border-sky-800',
    emerald: 'bg-emerald-950 text-emerald-300 border-emerald-800',
    rose: 'bg-rose-950 text-rose-300 border-rose-800',
  };

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-slate-700 transition relative overflow-hidden group">
      {/* Background radial glow */}
      <div className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full bg-sky-500/5 blur-2xl group-hover:bg-sky-500/10 transition" />

      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-xl border ${colorMap[color] || colorMap.sky}`}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold tracking-tight text-white">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {badge && (
          <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${badgeColorMap[color] || badgeColorMap.sky}`}>
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-slate-400">
          {subtitle}
        </p>
      )}
    </div>
  );
}
