import React from 'react';
import { ExternalLink, Globe, Phone, Mail, MapPin, Eye, Trash2, Calendar, Database, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

export default function LeadTable({
  leads = [],
  isLoading,
  total,
  page,
  pageSize,
  totalPages,
  onPageChange,
  onPageSizeChange,
  onSelectLead,
  onDeleteLead,
  onOpenScraper,
  onSeedDemo
}) {
  const getStatusBadge = (status) => {
    switch (status?.toUpperCase()) {
      case 'VERIFIED':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60';
      case 'NEW':
        return 'bg-sky-950/80 text-sky-400 border-sky-800/60';
      case 'CONTACTED':
        return 'bg-indigo-950/80 text-indigo-400 border-indigo-800/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 overflow-hidden shadow-xl">
      {/* Table container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/90 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <tr>
              <th scope="col" className="px-5 py-3.5">Clinic</th>
              <th scope="col" className="px-4 py-3.5">Location</th>
              <th scope="col" className="px-4 py-3.5">Website</th>
              <th scope="col" className="px-4 py-3.5">Contact</th>
              <th scope="col" className="px-4 py-3.5">Services</th>
              <th scope="col" className="px-3 py-3.5">AI Lead Score</th>
              <th scope="col" className="px-3 py-3.5">Status</th>
              <th scope="col" className="px-3 py-3.5">Source</th>
              <th scope="col" className="px-3 py-3.5">Created</th>
              <th scope="col" className="px-4 py-3.5 text-right">Actions</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {isLoading ? (
              // Loading skeleton
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="px-5 py-4">
                    <div className="h-4 bg-slate-800 rounded w-36 mb-1.5" />
                    <div className="h-3 bg-slate-800/60 rounded w-20" />
                  </td>
                  <td className="px-4 py-4"><div className="h-4 bg-slate-800 rounded w-24" /></td>
                  <td className="px-4 py-4"><div className="h-4 bg-slate-800 rounded w-28" /></td>
                  <td className="px-4 py-4"><div className="h-4 bg-slate-800 rounded w-24" /></td>
                  <td className="px-4 py-4"><div className="h-4 bg-slate-800 rounded w-32" /></td>
                  <td className="px-3 py-4"><div className="h-5 bg-slate-800 rounded-full w-14" /></td>
                  <td className="px-3 py-4"><div className="h-5 bg-slate-800 rounded-full w-14" /></td>
                  <td className="px-3 py-4"><div className="h-4 bg-slate-800 rounded w-16" /></td>
                  <td className="px-3 py-4"><div className="h-4 bg-slate-800 rounded w-16" /></td>
                  <td className="px-4 py-4 text-right"><div className="h-8 bg-slate-800 rounded w-16 ml-auto" /></td>
                </tr>
              ))
            ) : leads.length === 0 ? (
              // Empty state
              <tr>
                <td colSpan={10} className="px-6 py-16 text-center">
                  <div className="max-w-md mx-auto space-y-3">
                    <div className="h-12 w-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500">
                      <Globe className="h-6 w-6" />
                    </div>
                    <h3 className="text-base font-semibold text-white">No healthcare leads found</h3>
                    <p className="text-xs text-slate-400">
                      Discover public medical practices by scraping clinic websites, or load our pre-configured demo dataset.
                    </p>
                    <div className="pt-2 flex items-center justify-center space-x-3">
                      <button
                        onClick={onSeedDemo}
                        className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                      >
                        <Database className="h-3.5 w-3.5 text-sky-400" />
                        <span>Seed Demo Leads</span>
                      </button>
                      <button
                        onClick={onOpenScraper}
                        className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-sky-600 hover:bg-sky-500 text-white transition"
                      >
                        <Plus className="h-3.5 w-3.5" />
                        <span>Add Sources</span>
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            ) : (
              // Leads rows
              leads.map((lead) => (
                <tr
                  key={lead.id}
                  className="hover:bg-slate-900/50 transition cursor-pointer group"
                  onClick={() => onSelectLead(lead)}
                >
                  {/* Clinic Name & Specialty */}
                  <td className="px-5 py-3.5">
                    <div className="font-semibold text-white group-hover:text-sky-400 transition">
                      {lead.name}
                    </div>
                    <div className="text-[11px] font-medium text-slate-400 mt-0.5">
                      {lead.business_type || 'Clinic'}
                    </div>
                  </td>

                  {/* Location */}
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <div className="flex items-center space-x-1.5 text-xs text-slate-300">
                      <MapPin className="h-3.5 w-3.5 text-slate-500 flex-shrink-0" />
                      <span>{lead.city || '—'}{lead.state ? `, ${lead.state}` : ''}</span>
                    </div>
                    <div className="text-[11px] text-slate-500 pl-5">
                      {lead.country || 'Global'}
                    </div>
                  </td>

                  {/* Website */}
                  <td className="px-4 py-3.5" onClick={(e) => e.stopPropagation()}>
                    {lead.website ? (
                      <a
                        href={lead.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 text-xs text-sky-400 hover:text-sky-300 hover:underline max-w-[140px] truncate"
                        title={lead.website}
                      >
                        <Globe className="h-3.5 w-3.5 flex-shrink-0" />
                        <span className="truncate">{lead.normalized_website || lead.website.replace(/^https?:\/\//, '')}</span>
                        <ExternalLink className="h-2.5 w-2.5 flex-shrink-0 opacity-70" />
                      </a>
                    ) : (
                      <span className="text-xs text-slate-500">—</span>
                    )}
                  </td>

                  {/* Phone & Email */}
                  <td className="px-4 py-3.5 text-xs whitespace-nowrap">
                    {lead.phone ? (
                      <div className="flex items-center space-x-1 text-slate-300">
                        <Phone className="h-3 w-3 text-slate-500" />
                        <span>{lead.phone}</span>
                      </div>
                    ) : null}
                    {lead.email ? (
                      <div className="flex items-center space-x-1 text-slate-400 text-[11px] mt-0.5 truncate max-w-[140px]" title={lead.email}>
                        <Mail className="h-3 w-3 text-slate-500" />
                        <span className="truncate">{lead.email}</span>
                      </div>
                    ) : null}
                    {!lead.phone && !lead.email && <span className="text-slate-500">—</span>}
                  </td>

                  {/* Services tags */}
                  <td className="px-4 py-3.5">
                    {lead.services && lead.services.length > 0 ? (
                      <div className="flex flex-wrap gap-1 max-w-[200px]">
                        {lead.services.slice(0, 2).map((service, idx) => (
                          <span
                            key={idx}
                            className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60 truncate max-w-[120px]"
                          >
                            {service}
                          </span>
                        ))}
                        {lead.services.length > 2 && (
                          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] text-slate-400 bg-slate-900 border border-slate-800">
                            +{lead.services.length - 2}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">—</span>
                    )}
                  </td>

                  {/* AI Lead Score */}
                  <td className="px-3 py-3.5 whitespace-nowrap">
                    {lead.ai_score !== null && lead.ai_score !== undefined ? (
                      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                        lead.ai_score >= 80
                          ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60'
                          : lead.ai_score >= 60
                          ? 'bg-amber-950/80 text-amber-300 border-amber-700/60'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}>
                        <span>{lead.ai_score}</span>
                        <span className="text-[10px] font-medium opacity-80">• {lead.ai_score_category || 'Score'}</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-900 text-slate-500 border border-slate-800">
                        Not Analyzed
                      </span>
                    )}
                  </td>

                  {/* Status Badge */}
                  <td className="px-3 py-3.5 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusBadge(lead.status)}`}>
                      {lead.status || 'NEW'}
                    </span>
                  </td>

                  {/* Source */}
                  <td className="px-3 py-3.5 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                    <a
                      href={lead.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-[11px] text-slate-400 hover:text-slate-200"
                      title={lead.source_url}
                    >
                      <span>{lead.source_type || 'WEBSITE'}</span>
                      <ExternalLink className="h-2.5 w-2.5 opacity-60" />
                    </a>
                  </td>

                  {/* Created Date */}
                  <td className="px-3 py-3.5 whitespace-nowrap text-xs text-slate-400">
                    {formatDate(lead.created_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3.5 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-end space-x-1">
                      <button
                        onClick={() => onSelectLead(lead)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                        title="View Full Lead Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDeleteLead(lead.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition"
                        title="Delete Lead"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {!isLoading && leads.length > 0 && (
        <div className="px-5 py-3.5 bg-slate-900/60 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-slate-200 focus:outline-none focus:border-sky-500 cursor-pointer"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
            <span className="text-slate-500">|</span>
            <span>Page <strong className="text-slate-200">{page}</strong> of <strong className="text-slate-200">{totalPages}</strong> ({total} leads)</span>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
              title="Previous Page"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="px-2 font-medium text-slate-300">
              {page}
            </span>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
              title="Next Page"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
