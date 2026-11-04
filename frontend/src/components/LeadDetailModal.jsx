import React, { useState } from 'react';
import {
  X,
  ExternalLink,
  Globe,
  Phone,
  Mail,
  MapPin,
  Building,
  Sparkles,
  Check,
  Copy,
  Loader2,
  AlertCircle,
  Lightbulb,
  Send,
  TrendingUp,
  FileText
} from 'lucide-react';
import { analyzeLead, generateOutreach } from '../services/api';

export default function LeadDetailModal({ lead, onClose, onDelete, onLeadUpdated }) {
  const [copiedEmail, setCopiedEmail] = useState(false);
  const [copiedPhone, setCopiedPhone] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingOutreach, setIsGeneratingOutreach] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!lead) return null;

  const handleCopyPhone = () => {
    if (!lead.phone) return;
    navigator.clipboard.writeText(lead.phone);
    setCopiedPhone(true);
    setTimeout(() => setCopiedPhone(false), 2000);
  };

  const handleCopyEmailDraft = () => {
    if (!lead.ai_outreach_body) return;
    const fullText = `Subject: ${lead.ai_outreach_subject}\n\n${lead.ai_outreach_body}`;
    navigator.clipboard.writeText(fullText);
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2000);
  };

  const handleTriggerAnalysis = async () => {
    setErrorMessage('');
    setIsAnalyzing(true);
    try {
      const updated = await analyzeLead(lead.id);
      if (onLeadUpdated) onLeadUpdated(updated);
    } catch (err) {
      setErrorMessage(err.message || 'AI Analysis failed to process');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTriggerOutreach = async () => {
    setErrorMessage('');
    setIsGeneratingOutreach(true);
    try {
      const updated = await generateOutreach(lead.id);
      if (onLeadUpdated) onLeadUpdated(updated);
    } catch (err) {
      setErrorMessage(err.message || 'Outreach generation failed to process');
    } finally {
      setIsGeneratingOutreach(false);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    try {
      const d = new Date(isoString);
      return d.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch {
      return isoString;
    }
  };

  const getScoreColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'high':
        return 'text-emerald-400 bg-emerald-950/80 border-emerald-700/60';
      case 'medium':
        return 'text-amber-400 bg-amber-950/80 border-amber-700/60';
      default:
        return 'text-slate-400 bg-slate-900 border-slate-700';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-3 sm:p-5">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header banner */}
        <div className="bg-gradient-to-r from-sky-950/70 via-slate-900 to-indigo-950/70 p-6 border-b border-slate-800 flex items-start justify-between">
          <div className="space-y-1.5 max-w-xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-900/60 text-sky-300 border border-sky-700/60">
                {lead.business_type || 'Clinic'}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                {lead.status || 'NEW'}
              </span>
              {lead.ai_score !== null && lead.ai_score !== undefined && (
                <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold border ${getScoreColor(lead.ai_score_category)}`}>
                  <TrendingUp className="h-3 w-3" />
                  <span>AI Score: {lead.ai_score} ({lead.ai_score_category})</span>
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">{lead.name}</h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Action Toolbar */}
        <div className="px-6 py-3 bg-slate-950/70 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            {lead.ai_analyzed_at ? (
              <span>Last analyzed: {formatDate(lead.ai_analyzed_at)}</span>
            ) : (
              <span className="text-slate-500">Ready for AI growth analysis</span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleTriggerAnalysis}
              disabled={isAnalyzing}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-md shadow-sky-500/20 transition disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>{lead.ai_analysis ? 'Re-analyze with AI' : 'Analyze with AI'}</span>
                </>
              )}
            </button>

            <button
              onClick={handleTriggerOutreach}
              disabled={isGeneratingOutreach}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition disabled:opacity-50"
            >
              {isGeneratingOutreach ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Generating outreach...</span>
                </>
              ) : (
                <>
                  <Send className="h-3.5 w-3.5" />
                  <span>{lead.ai_outreach_body ? 'Regenerate Outreach' : 'Generate Outreach'}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 space-y-6 max-h-[72vh] overflow-y-auto">
          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* AI ANALYSIS SECTION */}
          {lead.ai_analysis && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 pb-1 border-b border-slate-800">
                <Sparkles className="h-4 w-4 text-sky-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">AI Intelligence & Opportunity Analysis</h3>
              </div>

              {/* AI Lead Score Card */}
              <div className="p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">AI Lead Score</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${getScoreColor(lead.ai_score_category)}`}>
                      {lead.ai_score_category}
                    </span>
                  </div>
                  <div className="text-2xl font-black text-white">
                    {lead.ai_score}<span className="text-sm font-normal text-slate-500">/100</span>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {lead.ai_score_reason}
                </p>
                <p className="text-[10px] text-slate-500 italic pt-1">
                  * Note: AI Lead Score is an automated assessment based on publicly available clinic data.
                </p>
              </div>

              {/* Business Info Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Identified Target Audience</div>
                  <p className="text-xs text-slate-200">{lead.ai_analysis.target_audience || 'Not enough information'}</p>
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Services Assessment</div>
                  <p className="text-xs text-slate-200">{lead.ai_analysis.services_summary || 'Standard clinical services'}</p>
                </div>
              </div>

              {/* Observations */}
              {lead.ai_analysis.observations && lead.ai_analysis.observations.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Key Observations</div>
                  <ul className="space-y-1.5">
                    {lead.ai_analysis.observations.map((obs, idx) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-sky-400 mt-1.5 flex-shrink-0" />
                        <span>{obs}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Opportunities (up to 3) */}
              {lead.ai_opportunities && lead.ai_opportunities.length > 0 && (
                <div className="space-y-2 pt-1">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                    <span>Identified Business Opportunities (Max 3)</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {lead.ai_opportunities.slice(0, 3).map((opp, idx) => (
                      <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800/90 space-y-1.5">
                        <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                          <span className="h-4 w-4 rounded-full bg-amber-500/20 text-amber-400 text-[10px] flex items-center justify-center flex-shrink-0 font-bold">
                            {idx + 1}
                          </span>
                          <span className="truncate">{opp.title}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">
                          <strong className="text-slate-300">Why: </strong>{opp.explanation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* PERSONALIZED OUTREACH DRAFT SECTION */}
          {lead.ai_outreach_body && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between pb-1 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <Send className="h-4 w-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Personalized Outreach Draft</h3>
                </div>
                <button
                  onClick={handleCopyEmailDraft}
                  className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                >
                  {copiedEmail ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied to Clipboard!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5 text-slate-400" />
                      <span>Copy Draft</span>
                    </>
                  )}
                </button>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-indigo-900/40 space-y-3">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Subject:</span>
                  <div className="text-xs font-semibold text-sky-300 mt-0.5">{lead.ai_outreach_subject}</div>
                </div>

                <div className="border-t border-slate-800/80 pt-3">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Email Body (100–150 words):</span>
                  <pre className="text-xs text-slate-200 font-sans whitespace-pre-wrap leading-relaxed mt-1.5 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    {lead.ai_outreach_body}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* Contact & Location Information */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Location card */}
            <div className="glass-card p-4 rounded-2xl border border-slate-800/80 space-y-1">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                <MapPin className="h-3.5 w-3.5 text-sky-400" />
                <span>Practice Location</span>
              </div>
              <p className="text-sm font-medium text-white">{lead.address || 'Address not listed'}</p>
              <p className="text-xs text-slate-300">
                {lead.city ? `${lead.city}, ` : ''}{lead.state ? `${lead.state} ` : ''}{lead.postal_code || ''}
              </p>
              <p className="text-xs text-slate-400">{lead.country || 'Global'}</p>
            </div>

            {/* Direct Contact info */}
            <div className="glass-card p-4 rounded-2xl border border-slate-800/80 space-y-2.5">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                <Building className="h-3.5 w-3.5 text-sky-400" />
                <span>Contact Channels</span>
              </div>

              {lead.phone ? (
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2 text-slate-300">
                    <Phone className="h-3.5 w-3.5 text-slate-500" />
                    <span>{lead.phone}</span>
                  </div>
                  <button
                    onClick={handleCopyPhone}
                    className="p-1 text-slate-500 hover:text-slate-300"
                    title="Copy phone"
                  >
                    {copiedPhone ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  </button>
                </div>
              ) : (
                <div className="text-xs text-slate-500">Phone: Not listed</div>
              )}

              {lead.email ? (
                <div className="flex items-center space-x-2 text-xs text-slate-300 truncate">
                  <Mail className="h-3.5 w-3.5 text-slate-500 flex-shrink-0" />
                  <span className="truncate">{lead.email}</span>
                </div>
              ) : (
                <div className="text-xs text-slate-500">Email: Not publicly listed</div>
              )}

              {lead.website ? (
                <div className="flex items-center space-x-2 text-xs pt-1 border-t border-slate-800/60">
                  <Globe className="h-3.5 w-3.5 text-sky-400 flex-shrink-0" />
                  <a
                    href={lead.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sky-400 hover:underline truncate flex items-center space-x-1"
                  >
                    <span className="truncate">{lead.website}</span>
                    <ExternalLink className="h-3 w-3 flex-shrink-0" />
                  </a>
                </div>
              ) : null}
            </div>
          </div>

          {/* Clinical Services */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Clinical Services & Offerings
            </h4>
            {lead.services && lead.services.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {lead.services.map((service, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-2.5 py-1 rounded-xl text-xs font-medium bg-slate-800/90 text-sky-300 border border-slate-700/80"
                  >
                    {service}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No specific services detected in public markup.</p>
            )}
          </div>

          {/* Description */}
          {lead.description && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Public Overview
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/50 p-3 rounded-2xl border border-slate-800/80">
                {lead.description}
              </p>
            </div>
          )}

          {/* Intelligence Provenance */}
          <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80 space-y-2 text-xs">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Source Provenance
            </h4>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-2 text-slate-400 truncate">
                <span>Source URL:</span>
                <a
                  href={lead.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sky-400 hover:underline truncate flex items-center space-x-1"
                >
                  <span className="truncate">{lead.source_url}</span>
                  <ExternalLink className="h-3 w-3 flex-shrink-0" />
                </a>
              </div>
              <span className="text-slate-500 whitespace-nowrap">
                Type: <strong className="text-slate-300">{lead.source_type}</strong>
              </span>
            </div>
          </div>
        </div>

        {/* Footer controls */}
        <div className="bg-slate-950 p-4 border-t border-slate-800 flex items-center justify-between">
          <button
            onClick={() => {
              if (window.confirm(`Are you sure you want to delete "${lead.name}"?`)) {
                onDelete(lead.id);
                onClose();
              }
            }}
            className="text-xs font-medium text-rose-400 hover:text-rose-300 transition"
          >
            Delete Lead
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-white transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
