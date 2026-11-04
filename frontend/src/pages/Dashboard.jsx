import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Database, Globe, CheckCircle2, AlertOctagon, Sparkles, TrendingUp, Send, CheckCircle } from 'lucide-react';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import FilterBar from '../components/FilterBar';
import LeadTable from '../components/LeadTable';
import LeadDetailModal from '../components/LeadDetailModal';
import ScraperModal from '../components/ScraperModal';
import { fetchLeads, fetchLeadStats, deleteLead, seedDemoLeads, checkHealth } from '../services/api';

export default function Dashboard() {
  // Leads & Pagination state
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  // Filters state
  const [search, setSearch] = useState('');
  const [city, setCity] = useState('all');
  const [country, setCountry] = useState('all');
  const [status, setStatus] = useState('all');
  const [businessType, setBusinessType] = useState('all');

  // Intelligence stats state
  const [stats, setStats] = useState({
    total_leads: 0,
    ai_analyzed: 0,
    high_potential: 0,
    outreach_ready: 0,
    websites_processed: 0,
    successful_records: 0,
    failed_records: 0,
    cities_count: 0
  });

  // UI modal states
  const [selectedLead, setSelectedLead] = useState(null);
  const [isScraperOpen, setIsScraperOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [apiHealth, setApiHealth] = useState('checking');
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Health check
  useEffect(() => {
    checkHealth()
      .then((res) => {
        setApiHealth(res.status === 'healthy' ? 'healthy' : 'degraded');
      })
      .catch(() => {
        setApiHealth('offline');
      });
  }, []);

  // Fetch Stats
  const loadStats = useCallback(async () => {
    try {
      const data = await fetchLeadStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load intelligence stats:', err);
    }
  }, []);

  // Fetch Leads
  const loadLeads = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchLeads({
        page,
        pageSize,
        search,
        city,
        country,
        status,
        businessType
      });
      setLeads(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Failed to load leads:', err);
      showToast(err.message || 'Failed to load leads', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, search, city, country, status, businessType]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadLeads();
    }, 250);
    return () => clearTimeout(timer);
  }, [loadLeads]);

  // Handle Seeding Demo
  const handleSeedDemo = async () => {
    setIsSeeding(true);
    try {
      const res = await seedDemoLeads();
      showToast(`Loaded ${res.created} demo healthcare businesses (${res.duplicates_skipped} duplicates skipped)!`, 'success');
      loadStats();
      loadLeads();
    } catch (err) {
      showToast(err.message || 'Failed to seed demo data', 'error');
    } finally {
      setIsSeeding(false);
    }
  };

  // Handle Deleting a Lead
  const handleDeleteLead = async (leadId) => {
    try {
      await deleteLead(leadId);
      showToast('Lead successfully removed from database', 'success');
      loadStats();
      loadLeads();
    } catch (err) {
      showToast(err.message || 'Failed to delete lead', 'error');
    }
  };

  // Reset Filters
  const handleResetFilters = () => {
    setSearch('');
    setCity('all');
    setCountry('all');
    setStatus('all');
    setBusinessType('all');
    setPage(1);
  };

  // Distinct cities list from current leads
  const distinctCities = useMemo(() => {
    const set = new Set();
    leads.forEach((l) => {
      if (l.city) set.add(l.city);
    });
    return Array.from(set).sort();
  }, [leads]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Toast notification */}
      {toast && (
        <div className="fixed top-5 right-5 z-50 animate-in slide-in-from-top-3 duration-200">
          <div className={`px-4 py-3 rounded-2xl shadow-2xl border text-xs font-medium flex items-center space-x-2 ${
            toast.type === 'error'
              ? 'bg-rose-950 text-rose-300 border-rose-800'
              : 'bg-emerald-950 text-emerald-300 border-emerald-800'
          }`}>
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Navigation */}
      <Navbar
        onOpenScraper={() => setIsScraperOpen(true)}
        onSeedDemo={handleSeedDemo}
        isSeeding={isSeeding}
        apiHealth={apiHealth}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-sky-950/70 text-sky-400 border border-sky-800/60 mb-2">
              <Sparkles className="h-3 w-3" />
              <span>AI Lead Intelligence Engine</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Healthcare Leads
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Aggregated, structured, and normalized intelligence from public medical business directories and clinic domains.
            </p>
          </div>
        </div>

        {/* Intelligence Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Leads"
            value={stats.total_leads}
            subtitle={`${stats.cities_count} distinct markets`}
            icon={Database}
            color="sky"
            badge="Discovered"
          />
          <StatCard
            title="AI Analyzed"
            value={stats.ai_analyzed}
            subtitle="Analyzed by AI model"
            icon={Sparkles}
            color="blue"
            badge="AI"
          />
          <StatCard
            title="High Potential"
            value={stats.high_potential}
            subtitle="AI Score >= 80"
            icon={TrendingUp}
            color="emerald"
            badge="Priority"
          />
          <StatCard
            title="Outreach Ready"
            value={stats.outreach_ready}
            subtitle="Personalized draft ready"
            icon={Send}
            color="amber"
            badge="Drafted"
          />
        </div>

        {/* Filter & Search Bar */}
        <FilterBar
          search={search}
          setSearch={(v) => { setSearch(v); setPage(1); }}
          city={city}
          setCity={(v) => { setCity(v); setPage(1); }}
          country={country}
          setCountry={(v) => { setCountry(v); setPage(1); }}
          status={status}
          setStatus={(v) => { setStatus(v); setPage(1); }}
          businessType={businessType}
          setBusinessType={(v) => { setBusinessType(v); setPage(1); }}
          onReset={handleResetFilters}
          citiesList={distinctCities}
          totalResults={total}
        />

        {/* Lead Table */}
        <LeadTable
          leads={leads}
          isLoading={isLoading}
          total={total}
          page={page}
          pageSize={pageSize}
          totalPages={totalPages}
          onPageChange={setPage}
          onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
          onSelectLead={setSelectedLead}
          onDeleteLead={handleDeleteLead}
          onOpenScraper={() => setIsScraperOpen(true)}
          onSeedDemo={handleSeedDemo}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>CareIntel AI — AI Healthcare Lead Intelligence & Outreach Platform | Recruiter-Ready Assessment</p>
      </footer>

      {/* Modals */}
      <LeadDetailModal
        lead={selectedLead}
        onClose={() => setSelectedLead(null)}
        onDelete={handleDeleteLead}
        onLeadUpdated={(updated) => {
          setSelectedLead(updated);
          loadStats();
          loadLeads();
          showToast(`AI analysis updated for "${updated.name}"`, 'success');
        }}
      />

      <ScraperModal
        isOpen={isScraperOpen}
        onClose={() => setIsScraperOpen(false)}
        onSuccess={() => {
          loadStats();
          loadLeads();
        }}
      />
    </div>
  );
}
