import React from 'react';
import { Activity, Plus, Database, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ onOpenScraper, onSeedDemo, isSeeding, apiHealth }) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 ring-1 ring-white/20">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold tracking-tight text-white">CareIntel<span className="text-sky-400">.ai</span></span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-sky-950/80 text-sky-400 border border-sky-800/60">
                Phase 1 MVP
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Healthcare Lead Discovery & Data Intelligence</p>
          </div>
        </div>

        {/* Action Controls & Health */}
        <div className="flex items-center space-x-3">
          {/* Health indicator */}
          <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-900 border border-slate-800 text-slate-300">
            <span className={`h-2 w-2 rounded-full ${apiHealth === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span>API {apiHealth === 'healthy' ? 'Online' : 'Connecting...'}</span>
          </div>

          {/* Seed Demo Button */}
          <button
            onClick={onSeedDemo}
            disabled={isSeeding}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-50"
            title="Load safe sample healthcare businesses into database"
          >
            <Database className="h-3.5 w-3.5 text-sky-400" />
            <span>{isSeeding ? 'Seeding...' : 'Seed Demo Data'}</span>
          </button>

          {/* Add Sources (Scraper) CTA */}
          <button
            onClick={onOpenScraper}
            className="inline-flex items-center space-x-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-md shadow-sky-500/20 transition hover:shadow-sky-500/30"
          >
            <Plus className="h-4 w-4" />
            <span>Add Sources</span>
          </button>
        </div>
      </div>
    </header>
  );
}
