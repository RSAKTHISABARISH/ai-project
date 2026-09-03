const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      let errorDetail = 'API request failed';
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorDetail;
      } catch (_) {}
      throw new Error(errorDetail);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // System Health & Metrics
  getHealth: () => request('/health'),
  getMetrics: () => request('/metrics'),
  getBusinessRules: () => request('/business-rules'),

  // Incidents
  getIncidents: (limit = 50) => request(`/incidents?limit=${limit}`),
  getIncident: (id) => request(`/incidents/${id}`),

  // PRs & Code Artifacts
  getPullRequests: (limit = 50) => request(`/pull-requests?limit=${limit}`),
  getPullRequest: (id) => request(`/pull-requests/${id}`),
  getDiffByPr: (prId) => request(`/diffs/by-pr/${prId}`),
  getReviewsByPr: (prId) => request(`/reviews/by-pr/${prId}`),

  // Events & Edge Cases
  getEvents: (limit = 50) => request(`/events?limit=${limit}`),
  getEventLogs: (limit = 50) => request(`/events/logs?limit=${limit}`),
  ingestEvent: (data) => request('/events', { method: 'POST', body: JSON.stringify(data) }),
  injectDuplicate: () => request('/events/inject-duplicate', { method: 'POST' }),
  injectDelayed: () => request('/events/inject-delayed', { method: 'POST' }),
  injectOutOfOrder: () => request('/events/inject-out-of-order', { method: 'POST' }),

  // Runbooks & AI Generation
  generateRunbook: (incidentId, prId = null, forceDemo = false) =>
    request('/runbooks/generate', {
      method: 'POST',
      body: JSON.stringify({ incident_id: incidentId, pr_id: prId, force_demo_mode: forceDemo }),
    }),
  getRunbooks: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/runbooks${query ? `?${query}` : ''}`);
  },
  getRunbook: (id) => request(`/runbooks/${id}`),
  searchRunbooks: (q) => request(`/runbooks/search?q=${encodeURIComponent(q)}`),

  // Approvals & Human Override
  approveRunbook: (id, payload) =>
    request(`/runbooks/${id}/approve`, { method: 'POST', body: JSON.stringify(payload) }),
  rejectRunbook: (id, payload) =>
    request(`/runbooks/${id}/reject`, { method: 'POST', body: JSON.stringify(payload) }),
  overrideRunbook: (id, payload) =>
    request(`/runbooks/${id}/override`, { method: 'POST', body: JSON.stringify(payload) }),
  getOverrideHistory: (id) => request(`/runbooks/${id}/overrides`),

  // Demo Scenarios
  seedDemoData: (forceReset = false) =>
    request(`/demo/seed?force_reset=${forceReset}`, { method: 'POST' }),
  loadScenarioInc052: () => request('/demo/scenario-inc052', { method: 'POST' }),
};
