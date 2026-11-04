// Dynamic API Base URL configuration: supports VITE_API_URL and VITE_API_BASE_URL
const rawBase = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').trim();
const cleanBase = rawBase.replace(/\/+$/, '');
const API_BASE_URL = cleanBase.endsWith('/api/v1') ? cleanBase : `${cleanBase}/api/v1`;

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP ${response.status} Error`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorData.message || errorMsg;
    } catch {
      // response was not JSON
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return handleResponse(res);
}

export async function fetchLeads({
  page = 1,
  pageSize = 20,
  search = '',
  city = '',
  country = '',
  status = '',
  businessType = ''
} = {}) {
  const query = new URLSearchParams();
  query.append('page', page);
  query.append('page_size', pageSize);

  if (search.trim()) query.append('search', search.trim());
  if (city.trim() && city !== 'all') query.append('city', city.trim());
  if (country.trim() && country !== 'all') query.append('country', country.trim());
  if (status.trim() && status !== 'all') query.append('status', status.trim());
  if (businessType.trim() && businessType !== 'all') query.append('business_type', businessType.trim());

  const res = await fetch(`${API_BASE_URL}/leads?${query.toString()}`);
  return handleResponse(res);
}

export async function fetchLeadStats() {
  const res = await fetch(`${API_BASE_URL}/leads/stats`);
  return handleResponse(res);
}

export async function fetchLeadById(leadId) {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}`);
  return handleResponse(res);
}

export async function deleteLead(leadId) {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}`, {
    method: 'DELETE'
  });
  return handleResponse(res);
}

export async function scrapeUrls(urls) {
  const res = await fetch(`${API_BASE_URL}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ urls })
  });
  return handleResponse(res);
}

export async function scrapeCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/scrape/csv`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}

export async function seedDemoLeads() {
  const res = await fetch(`${API_BASE_URL}/leads/seed-demo`, {
    method: 'POST'
  });
  return handleResponse(res);
}

export async function analyzeLead(leadId) {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}/analyze`, {
    method: 'POST'
  });
  return handleResponse(res);
}

export async function generateOutreach(leadId) {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}/generate-outreach`, {
    method: 'POST'
  });
  return handleResponse(res);
}
