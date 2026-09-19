const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '');
const ORGANIZATION_ID = import.meta.env.VITE_ORGANIZATION_ID || '';
const TOKEN_KEY = 'ai-reception.access-token';

export interface BackendAIResponse {
  answer: string;
  intent: string;
  confidence: number;
  action: 'answer_question' | 'book_appointment' | 'create_ticket' | 'human_handoff' | 'get_department' | null;
  needs_human: boolean;
  language: 'en';
  sources: Array<Record<string, string>>;
}

export interface BackendConversationCreated {
  conversation_id: string;
  visitor_id: string;
  status: string;
  channel: string;
}

export interface BackendMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  language: string;
  intent: string | null;
  confidence: number | null;
  created_at: string;
}

export interface BackendMessageResponse {
  message: BackendMessage;
  ai_response: BackendAIResponse;
}

export interface BackendConversation {
  id: string;
  organization_id: string;
  visitor_id: string;
  channel: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  assigned_department: string | null;
  messages: BackendMessage[];
}

export interface BackendAppointment {
  id: string;
  organization_id: string;
  conversation_id: string | null;
  visitor_id: string;
  department_id: string;
  requested_staff: string | null;
  appointment_date: string;
  appointment_time: string;
  purpose: string;
  status: string;
  created_at: string;
}

export interface BackendTicket {
  id: string;
  organization_id: string;
  conversation_id: string | null;
  visitor_id: string;
  department_id: string;
  category: string | null;
  title: string;
  description: string;
  priority: string;
  status: string;
  assigned_user: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendDepartment {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  contact: string | null;
  location: string | null;
  active: boolean;
}

export interface BackendVisitor {
  id: string;
  code: string;
  name: string;
  first_seen: string;
  last_interaction: string;
  purpose: string;
  department: string;
  status: 'Active' | 'Completed' | 'Needs staff';
  channel: 'Reception Kiosk' | 'Phone Call';
  duration: string;
}

export interface BackendAnalytics {
  visitors_by_hour: Array<{ hour: string; count: number }>;
  top_intents: Array<{ intent: string; count: number }>;
  department_demand: Array<{ department: string; requests: number }>;
  channel_usage: Array<{ name: string; value: number }>;
  outcomes: Array<{ outcome: string; percentage: number }>;
}

export function getOrganizationId(): string {
  if (!ORGANIZATION_ID) {
    throw new Error('VITE_ORGANIZATION_ID is not configured.');
  }
  return ORGANIZATION_ID;
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

async function request<T>(path: string, options: RequestInit = {}, authenticated = false): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const token = getAccessToken();
  if (authenticated && token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error?.message || body?.detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body as T;
}

export const apiClient = {
  startConversation(visitor: { name?: string; phone?: string; email?: string; channel?: string } = {}) {
    return request<BackendConversationCreated>('/conversations', {
      method: 'POST',
      body: JSON.stringify({ organization_id: getOrganizationId(), preferred_language: 'en', channel: 'web', ...visitor }),
    });
  },
  sendMessage(conversationId: string, content: string) {
    return request<BackendMessageResponse>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, language: 'en' }),
    });
  },
  getConversation(conversationId: string) {
    return request<BackendConversation>(`/conversations/${conversationId}`);
  },
  listConversations() {
    return request<BackendConversation[]>('/conversations', {}, true);
  },
  listAppointments() {
    return request<BackendAppointment[]>('/appointments', {}, true);
  },
  updateAppointment(id: string, status: string) {
    return request<BackendAppointment>(`/appointments/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: status.toLowerCase() }),
    }, true);
  },
  listTickets() {
    return request<BackendTicket[]>('/tickets', {}, true);
  },
  updateTicket(id: string, status: string) {
    return request<BackendTicket>(`/tickets/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: status.toLowerCase().replace(' ', '_') }),
    }, true);
  },
  listDepartments() {
    return request<BackendDepartment[]>(`/departments?organization_id=${encodeURIComponent(getOrganizationId())}`, {}, true);
  },
  listVisitors() {
    return request<BackendVisitor[]>('/visitors', {}, true);
  },
  getAnalytics(timeframe: string) {
    return request<BackendAnalytics>(`/analytics?timeframe=${encodeURIComponent(timeframe)}`, {}, true);
  },
  login(email: string, password: string) {
    const form = new URLSearchParams({ username: email, password });
    return request<{ access_token: string }>('/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    }).then((result) => {
      setAccessToken(result.access_token);
      return result;
    });
  },
};
