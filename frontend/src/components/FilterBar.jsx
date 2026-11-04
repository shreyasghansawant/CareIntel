import React from 'react';
import { Search, X, RotateCcw, Filter, MapPin, Tag, Stethoscope } from 'lucide-react';

export default function FilterBar({
  search,
  setSearch,
  city,
  setCity,
  country,
  setCountry,
  status,
  setStatus,
  businessType,
  setBusinessType,
  onReset,
  citiesList = [],
  totalResults = 0
}) {
  const hasActiveFilters = Boolean(
    search || (city && city !== 'all') || (country && country !== 'all') || (status && status !== 'all') || (businessType && businessType !== 'all')
  );

  return (
    <div className="glass-panel rounded-2xl p-4 border border-slate-800/80 mb-6 space-y-3">
      <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center justify-between">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search clinics, treatments, services, cities..."
            className="w-full pl-10 pr-9 py-2 rounded-xl text-sm bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Filter Dropdowns */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {/* Business Type */}
          <div className="relative">
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="w-full appearance-none pl-3 pr-8 py-2 rounded-xl text-xs font-medium bg-slate-900 border border-slate-700/80 text-slate-200 focus:outline-none focus:border-sky-500 cursor-pointer"
            >
              <option value="all">All Specialties</option>
              <option value="Dental Clinic">Dental Clinic</option>
              <option value="Physiotherapy & Rehab">Physiotherapy</option>
              <option value="Dermatology & Skin">Dermatology</option>
              <option value="Chiropractic & Spine">Chiropractic</option>
              <option value="Optometry & Eye Care">Optometry</option>
              <option value="Pediatric Care">Pediatrics</option>
              <option value="Mental Health & Wellness">Mental Health</option>
              <option value="Medical Center / Hospital">Medical Center</option>
            </select>
            <Stethoscope className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
          </div>

          {/* City */}
          <div className="relative">
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full appearance-none pl-3 pr-8 py-2 rounded-xl text-xs font-medium bg-slate-900 border border-slate-700/80 text-slate-200 focus:outline-none focus:border-sky-500 cursor-pointer"
            >
              <option value="all">All Cities</option>
              {citiesList.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <MapPin className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
          </div>

          {/* Status */}
          <div className="relative">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full appearance-none pl-3 pr-8 py-2 rounded-xl text-xs font-medium bg-slate-900 border border-slate-700/80 text-slate-200 focus:outline-none focus:border-sky-500 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="NEW">NEW</option>
              <option value="VERIFIED">VERIFIED</option>
              <option value="CONTACTED">CONTACTED</option>
              <option value="UNQUALIFIED">UNQUALIFIED</option>
            </select>
            <Tag className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
          </div>

          {/* Reset Filters */}
          <button
            onClick={onReset}
            disabled={!hasActiveFilters}
            className="flex items-center justify-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Results counter indicator */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/40">
        <span>Showing <strong className="text-slate-200">{totalResults}</strong> discovered healthcare leads</span>
        {hasActiveFilters && (
          <span className="text-sky-400 font-medium">Filtered view active</span>
        )}
      </div>
    </div>
  );
}
