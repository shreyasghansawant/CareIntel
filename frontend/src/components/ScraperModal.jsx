import React, { useState } from 'react';
import { X, Plus, Trash2, Globe, UploadCloud, CheckCircle2, XCircle, AlertCircle, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { scrapeUrls, scrapeCsv } from '../services/api';

export default function ScraperModal({ isOpen, onClose, onSuccess }) {
  const [mode, setMode] = useState('list'); // 'list' | 'bulk' | 'csv'
  const [urlList, setUrlList] = useState(['https://www.apexdentalstudio.com', 'https://www.harborviewpt.com']);
  const [bulkText, setBulkText] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [scrapeResponse, setScrapeResponse] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleAddUrlRow = () => {
    setUrlList([...urlList, '']);
  };

  const handleUrlChange = (index, value) => {
    const updated = [...urlList];
    updated[index] = value;
    setUrlList(updated);
  };

  const handleRemoveUrlRow = (index) => {
    if (urlList.length <= 1) {
      setUrlList(['']);
      return;
    }
    setUrlList(urlList.filter((_, i) => i !== index));
  };

  const handleStartProcessing = async () => {
    setErrorMessage('');
    setScrapeResponse(null);

    let urlsToProcess = [];
    if (mode === 'list') {
      urlsToProcess = urlList.map((u) => u.trim()).filter(Boolean);
    } else if (mode === 'bulk') {
      urlsToProcess = bulkText
        .split('\n')
        .map((u) => u.trim())
        .filter(Boolean);
    }

    if (mode !== 'csv' && urlsToProcess.length === 0) {
      setErrorMessage('Please enter at least one public healthcare website URL');
      return;
    }

    if (mode === 'csv' && !csvFile) {
      setErrorMessage('Please select a CSV file containing website URLs');
      return;
    }

    setIsProcessing(true);
    try {
      let res;
      if (mode === 'csv') {
        res = await scrapeCsv(csvFile);
      } else {
        res = await scrapeUrls(urlsToProcess);
      }
      setScrapeResponse(res);
      onSuccess();
    } catch (err) {
      setErrorMessage(err.message || 'Scraping workflow encountered an error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setScrapeResponse(null);
    setErrorMessage('');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-gradient-to-r from-sky-950/60 via-slate-900 to-indigo-950/60 p-6 border-b border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Discovery Engine</span>
            <h2 className="text-xl font-bold text-white tracking-tight">Add Healthcare Sources</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          {!scrapeResponse && (
            <>
              {/* Mode switch */}
              <div className="flex p-1 bg-slate-950 rounded-xl border border-slate-800 text-xs font-medium">
                <button
                  type="button"
                  onClick={() => setMode('list')}
                  className={`flex-1 py-1.5 rounded-lg transition ${mode === 'list' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  Individual URLs
                </button>
                <button
                  type="button"
                  onClick={() => setMode('bulk')}
                  className={`flex-1 py-1.5 rounded-lg transition ${mode === 'bulk' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  Bulk Paste (Multiline)
                </button>
                <button
                  type="button"
                  onClick={() => setMode('csv')}
                  className={`flex-1 py-1.5 rounded-lg transition ${mode === 'csv' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  Upload CSV
                </button>
              </div>

              {/* Mode 1: Individual URL list */}
              {mode === 'list' && (
                <div className="space-y-3">
                  <div className="space-y-2">
                    {urlList.map((url, idx) => (
                      <div key={idx} className="flex items-center space-x-2">
                        <div className="relative flex-1">
                          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                          <input
                            type="url"
                            value={url}
                            onChange={(e) => handleUrlChange(idx, e.target.value)}
                            placeholder="https://example-clinic.com"
                            className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700/80 text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 transition"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveUrlRow(idx)}
                          className="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition"
                          title="Remove URL"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={handleAddUrlRow}
                    className="inline-flex items-center space-x-1.5 text-xs font-semibold text-sky-400 hover:text-sky-300 py-1"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    <span>+ Add another</span>
                  </button>
                </div>
              )}

              {/* Mode 2: Bulk paste */}
              {mode === 'bulk' && (
                <div className="space-y-2">
                  <label className="text-xs text-slate-400">Paste one URL per line:</label>
                  <textarea
                    rows={6}
                    value={bulkText}
                    onChange={(e) => setBulkText(e.target.value)}
                    placeholder={`https://austindentalsmile.com\nhttps://sydneyphysio.com.au\nhttps://kensingtonpediatrics.co.uk`}
                    className="w-full p-3 rounded-2xl text-xs bg-slate-950 border border-slate-700/80 text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 font-mono transition"
                  />
                </div>
              )}

              {/* Mode 3: CSV upload */}
              {mode === 'csv' && (
                <div className="space-y-3">
                  <div className="border-2 border-dashed border-slate-700 rounded-2xl p-6 text-center hover:border-sky-500/60 transition bg-slate-950/40">
                    <UploadCloud className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-xs font-medium text-slate-200">
                      {csvFile ? csvFile.name : 'Upload CSV containing healthcare URLs'}
                    </p>
                    <p className="text-[11px] text-slate-500 mt-1">
                      File should contain a column with URLs
                    </p>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                      className="hidden"
                      id="csv-file-upload"
                    />
                    <label
                      htmlFor="csv-file-upload"
                      className="mt-3 inline-block px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 cursor-pointer border border-slate-700"
                    >
                      Browse File
                    </label>
                  </div>
                </div>
              )}

              {/* Privacy and scope note */}
              <div className="text-[11px] text-slate-500 bg-slate-950/50 p-3 rounded-xl border border-slate-800/80">
                <span className="font-semibold text-slate-400">Ethical Public Scraper:</span> Collects only publicly accessible business contact details, services, and location markup. Does not bypass logins, paywalls, or private repositories.
              </div>
            </>
          )}

          {/* Error banner */}
          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Real-time Processing / Results Feedback */}
          {isProcessing && (
            <div className="p-8 text-center space-y-3">
              <Loader2 className="h-8 w-8 text-sky-400 animate-spin mx-auto" />
              <h4 className="text-sm font-semibold text-white">Processing healthcare sources...</h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                CareIntel scraper is fetching HTML markup, extracting Schema.org structured data, and normalizing business fields.
              </p>
            </div>
          )}

          {scrapeResponse && (
            <div className="space-y-4">
              {/* Summary Cards */}
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Processing Summary</h4>
                <div className="grid grid-cols-3 gap-2 text-center pt-1">
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <div className="text-base font-bold text-white">✓ {scrapeResponse.processed}</div>
                    <div className="text-[10px] text-slate-400">sources processed</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-800/50">
                    <div className="text-base font-bold text-emerald-400">✓ {scrapeResponse.leads_created}</div>
                    <div className="text-[10px] text-emerald-300">leads created</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-800/50">
                    <div className="text-base font-bold text-rose-400">✕ {scrapeResponse.failed}</div>
                    <div className="text-[10px] text-rose-300">sources failed</div>
                  </div>
                </div>
                {scrapeResponse.duplicates_skipped > 0 && (
                  <p className="text-[11px] text-amber-400/90 text-center pt-1">
                    ℹ {scrapeResponse.duplicates_skipped} duplicate source(s) detected and merged.
                  </p>
                )}
              </div>

              {/* Per-URL Breakdown */}
              <div className="space-y-2">
                <h5 className="text-xs font-semibold text-slate-400">Detailed Source Extraction Log</h5>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {scrapeResponse.results.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between text-xs gap-3"
                    >
                      <div className="truncate flex-1">
                        <div className="font-medium text-white truncate">{item.name || item.url}</div>
                        <div className="text-[11px] text-slate-500 truncate">{item.url}</div>
                        {item.error && (
                          <div className="text-[11px] text-rose-400 mt-0.5">{item.error}</div>
                        )}
                      </div>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold uppercase flex-shrink-0 border ${
                          item.status === 'created'
                            ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                            : item.status === 'duplicate_skipped'
                            ? 'bg-amber-950 text-amber-400 border-amber-800'
                            : 'bg-rose-950 text-rose-400 border-rose-800'
                        }`}
                      >
                        {item.status === 'created' ? 'Created' : item.status === 'duplicate_skipped' ? 'Duplicate' : 'Failed'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer controls */}
        <div className="bg-slate-950 p-4 border-t border-slate-800 flex items-center justify-between">
          {scrapeResponse ? (
            <>
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                <span>Process More</span>
              </button>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold rounded-xl bg-sky-600 hover:bg-sky-500 text-white transition shadow-md shadow-sky-600/20"
              >
                View Leads in Dashboard
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={onClose}
                disabled={isProcessing}
                className="text-xs text-slate-400 hover:text-white transition disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleStartProcessing}
                disabled={isProcessing}
                className="inline-flex items-center space-x-2 px-5 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white transition shadow-lg shadow-sky-500/20 disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>Start Processing</span>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
