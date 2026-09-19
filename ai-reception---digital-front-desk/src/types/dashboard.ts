import { KnowledgeSource } from './reception';

export interface DashboardMetric {
  title: string;
  value: number | string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  subtext: string;
}

export interface LiveEventItem {
  id: string;
  time: string;
  type:
    | 'visitor_detected'
    | 'session_started'
    | 'listening'
    | 'transcript'
    | 'intent_classified'
    | 'source_retrieved'
    | 'answer_delivered'
    | 'appointment_booked'
    | 'ticket_created'
    | 'handoff_requested'
    | 'session_ended';
  description: string;
  metadata?: Record<string, any>;
}

export interface ConversationItem {
  id: string;
  visitorId: string;
  visitorName?: string;
  channel: 'Reception' | 'Phone';
  intent: string;
  startedAt: string;
  duration: string;
  status: 'Active' | 'Completed' | 'Human handoff';
  language: 'ne' | 'en';
  messageCount: number;
  messages: Array<{
    id: string;
    sender: 'USER' | 'AI' | 'SYSTEM' | 'STAFF';
    text: string;
    timestamp: string;
    sources?: KnowledgeSource[];
  }>;
  sourcesUsed: KnowledgeSource[];
  actionTaken?: string;
}

export interface VisitorRecord {
  id: string;
  code: string;
  firstSeen: string;
  lastInteraction: string;
  purpose: string;
  department: string;
  status: 'Active' | 'Completed' | 'Needs staff';
  channel: 'Reception Kiosk' | 'Phone Call';
  duration: string;
}

export interface AppointmentRecord {
  id: string;
  referenceCode: string;
  visitorName: string;
  contact: string;
  targetPerson: string;
  department: string;
  date: string;
  timeSlot: string;
  purpose: string;
  status: 'Confirmed' | 'Pending' | 'Completed' | 'Cancelled';
  createdAt: string;
}

export interface TicketRecord {
  id: string;
  ticketId: string;
  issue: string;
  department: string;
  priority: 'Low' | 'Normal' | 'High';
  status: 'Open' | 'In Progress' | 'Resolved';
  visitorName: string;
  contact: string;
  assignedStaff: string;
  createdAt: string;
}

export interface KnowledgeDocument {
  id: string;
  name: string;
  size: string;
  pages: number;
  status: 'Indexed' | 'Processing' | 'Failed';
  uploadedAt: string;
  lastIndexed: string;
  department: string;
}

export interface AnalyticsData {
  visitorsByHour: Array<{ hour: string; count: number }>;
  topIntents: Array<{ intent: string; count: number }>;
  departmentDemand: Array<{ department: string; requests: number }>;
  channelUsage: Array<{ name: string; value: number }>;
  outcomes: Array<{ outcome: string; percentage: number }>;
}

export interface OrganizationSettings {
  name: string;
  code: string;
  address: string;
  contactPhone: string;
  contactEmail: string;
  operatingHours: string;
  kioskId: string;
  greetingEn: string;
  greetingNe: string;
  fallbackResponse: string;
  handoffDutyDesk: string;
  cameraDetectionEnabled: boolean;
  privacyMode: boolean;
  speechRate: number;
}
