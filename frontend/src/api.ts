export type DiagnosisResult = {
  root_cause: string;
  confidence: number;
  osi_layer: string;
  evidence: string[];
  next_command: string[];
  fix_steps: string[];
  verification: string[];
  human_review: { status: string; reason: string };
};

export type DiagnosisRecord = {
  id: number;
  case_id: string | null;
  symptom: string;
  topology_note: string;
  show_outputs: string;
  engine: string;
  review_status: string;
  created_at: string;
  result: DiagnosisResult;
};

export type CaseListItem = {
  case_id: string;
  issue_type: string;
  symptom: string;
  severity: string;
  osi_layer: string;
  concept: string;
  review_status: string;
};

export type CaseDetail = CaseListItem & {
  topology_note: string;
  show_outputs: string;
  expected_fault: string;
  latest_diagnosis: DiagnosisRecord | null;
};

export type DashboardData = {
  total_cases: number;
  by_issue_type: Record<string, number>;
  critical: number;
  high: number;
  medium: number;
  low: number;
  accepted: number;
  edited: number;
  rejected: number;
  reviewed: number;
  agreement_rate: number | null;
  agreement_label: string;
};

export type RaiRecord = {
  id: number;
  case_id: string;
  initial_ai_diagnosis: string;
  human_correction: string;
  why_incorrect: string;
  evidence_used: string;
  final_decision: string;
  final_approved_diagnosis: string;
  is_template: boolean;
  created_at: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      ...init,
    });
  } catch {
    throw new Error("Backend is not reachable. Start the FastAPI server on port 8000.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = (data as { detail?: string }).detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data as T;
}

export const api = {
  health: () => request<{ ok: boolean }>("/api/health"),
  dashboard: () => request<DashboardData>("/api/dashboard"),
  cases: (params: Record<string, string>) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v) q.set(k, v);
    });
    return request<{ items: CaseListItem[]; count: number }>(`/api/cases?${q.toString()}`);
  },
  case: (id: string) => request<CaseDetail>(`/api/cases/${encodeURIComponent(id)}`),
  analyze: (body: {
    case_id?: string;
    symptom: string;
    topology_note: string;
    show_outputs: string;
  }) =>
    request<DiagnosisRecord>("/api/analyze", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  review: (body: {
    diagnosis_id: number;
    decision: string;
    reviewer_comment: string;
    human_correction: string;
  }) => request("/api/reviews", { method: "POST", body: JSON.stringify(body) }),
  resetCase: (id: string) =>
    request(`/api/cases/${encodeURIComponent(id)}/reset`, { method: "POST" }),
  rai: () => request<{ items: RaiRecord[] }>("/api/responsible-ai"),
  ruleCheck: (state?: object) =>
    request<{
      report: string;
      findings: { level: string; message: string; detail: string }[];
    }>("/api/rule-check", { method: "POST", body: JSON.stringify({ state: state ?? null }) }),
};
