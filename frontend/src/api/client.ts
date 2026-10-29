import {
  Defect,
  Investigation,
  InvestigationEvent,
  Evidence,
  Reproduction,
  RegressionTest,
  TestRun,
  Release,
  ReleaseCheck,
  DatabaseChange,
  AuditLogItem,
  DashboardMetrics,
  SystemHealth
} from '../types';

const BASE_URL = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData.message) errorMsg = errData.message;
      else if (errData.detail) errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<SystemHealth>('/health'),

  // Reports & Dashboard
  getDashboardMetrics: () => fetchJson<DashboardMetrics>('/reports/dashboard'),
  getReportView: (reportName: string) => fetchJson<any>(`/reports/view/${reportName}`),

  // Defects
  getDefects: (params?: { skip?: number; limit?: number; severity?: string; status?: string; component?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.skip !== undefined) query.set('skip', params.skip.toString());
    if (params?.limit !== undefined) query.set('limit', params.limit.toString());
    if (params?.severity) query.set('severity', params.severity);
    if (params?.status) query.set('status', params.status);
    if (params?.component) query.set('component', params.component);
    if (params?.search) query.set('search', params.search);
    return fetchJson<{ items: Defect[]; total: number; page: number; page_size: number }>(`/defects?${query.toString()}`);
  },
  getDefect: (id: string) => fetchJson<Defect>(`/defects/${id}`),
  createDefect: (defect: Partial<Defect>) => fetchJson<Defect>('/defects', { method: 'POST', body: JSON.stringify(defect) }),
  updateDefect: (id: string, updates: Partial<Defect>) => fetchJson<Defect>(`/defects/${id}`, { method: 'PUT', body: JSON.stringify(updates) }),
  transitionDefect: (id: string, target_status: string, actor: string, reason: string) =>
    fetchJson<Defect>(`/defects/${id}/transition`, {
      method: 'POST',
      body: JSON.stringify({ target_status, actor, reason }),
    }),

  // Reproductions & Evidence
  getReproductions: (defectId: string) => fetchJson<Reproduction[]>(`/defects/${defectId}/reproductions`),
  addReproduction: (defectId: string, data: Partial<Reproduction>) =>
    fetchJson<Reproduction>(`/defects/${defectId}/reproductions`, { method: 'POST', body: JSON.stringify(data) }),
  getEvidence: (defectId: string) => fetchJson<Evidence[]>(`/defects/${defectId}/evidence`),
  addEvidence: (defectId: string, data: Partial<Evidence>) =>
    fetchJson<Evidence>(`/defects/${defectId}/evidence`, { method: 'POST', body: JSON.stringify(data) }),

  // Investigations
  getInvestigationByDefect: (defectId: string) => fetchJson<Investigation>(`/investigations/defect/${defectId}`),
  createInvestigation: (data: Partial<Investigation>) => fetchJson<Investigation>('/investigations', { method: 'POST', body: JSON.stringify(data) }),
  updateInvestigation: (id: string, updates: Partial<Investigation>) => fetchJson<Investigation>(`/investigations/${id}`, { method: 'PUT', body: JSON.stringify(updates) }),
  addInvestigationEvent: (id: string, event: Partial<InvestigationEvent>) => fetchJson<InvestigationEvent>(`/investigations/${id}/events`, { method: 'POST', body: JSON.stringify(event) }),

  // Testing & Runs
  getRegressionTests: () => fetchJson<RegressionTest[]>('/testing/tests'),
  getTestRuns: (params?: { limit?: number; related_defect_id?: string; related_release_id?: string }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.related_defect_id) query.set('related_defect_id', params.related_defect_id);
    if (params?.related_release_id) query.set('related_release_id', params.related_release_id);
    return fetchJson<TestRun[]>(`/testing/runs?${query.toString()}`);
  },
  executeTest: (command: string, related_defect_id?: string, related_release_id?: string, triggered_by = 'developer') =>
    fetchJson<TestRun>('/testing/runs/execute', {
      method: 'POST',
      body: JSON.stringify({ command, related_defect_id, related_release_id, triggered_by }),
    }),

  // Releases
  getReleases: () => fetchJson<Release[]>('/releases'),
  getRelease: (id: string) => fetchJson<Release>(`/releases/${id}`),
  updateReleaseCheck: (releaseId: string, checkId: string, data: Partial<ReleaseCheck>) =>
    fetchJson<ReleaseCheck>(`/releases/${releaseId}/checks/${checkId}`, { method: 'PUT', body: JSON.stringify(data) }),
  evaluateRelease: (releaseId: string) => fetchJson<any>(`/releases/${releaseId}/evaluate`, { method: 'POST' }),

  // Database Changes
  getDatabaseChanges: () => fetchJson<DatabaseChange[]>('/database-changes'),
  executeDatabaseChange: (id: string, applied_by = 'dba.engineer') =>
    fetchJson<any>(`/database-changes/${id}/execute?applied_by=${encodeURIComponent(applied_by)}`, { method: 'POST' }),

  // Audit
  getAuditLogs: (params?: { entity_type?: string; entity_id?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.entity_type) query.set('entity_type', params.entity_type);
    if (params?.entity_id) query.set('entity_id', params.entity_id);
    if (params?.limit) query.set('limit', params.limit.toString());
    return fetchJson<AuditLogItem[]>(`/audit?${query.toString()}`);
  },

  // TracePoint Lab
  runScenarioA: (start = '2026-09-01', end = '2026-09-30', mode = 'buggy') =>
    fetchJson<any>(`/lab/scenarios/date-boundary?start=${start}&end=${end}&mode=${mode}`),
  runScenarioB: (orderId = 'ORD-99', mode = 'buggy') =>
    fetchJson<any>(`/lab/scenarios/duplicate-aggregation?order_id=${orderId}&mode=${mode}`),
  runScenarioC: (current_status = 'DRAFT', target_status = 'ISSUED', amount = 75000, credit_approved = false, mode = 'buggy') =>
    fetchJson<any>('/lab/scenarios/invoice-transition', {
      method: 'POST',
      body: JSON.stringify({ current_status, target_status, amount, credit_approved, mode }),
    }),
  runScenarioD: (mode = 'buggy') =>
    fetchJson<any>(`/lab/scenarios/batch-settlement?mode=${mode}`, { method: 'POST' }),
  runScenarioE: (order_amount = 100, coupon_code = 'SUMMER20', coupon_expiry_date = '2026-06-01', mode = 'buggy') =>
    fetchJson<any>('/lab/scenarios/discount-calculation', {
      method: 'POST',
      body: JSON.stringify({ order_amount, coupon_code, coupon_expiry_date, mode }),
    }),
};
