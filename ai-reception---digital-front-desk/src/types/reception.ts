export type ReceptionState =
  | 'IDLE'
  | 'VISITOR_DETECTED'
  | 'LISTENING'
  | 'THINKING'
  | 'SPEAKING'
  | 'ACTION_APPOINTMENT'
  | 'ACTION_TICKET'
  | 'HANDOFF'
  | 'UNKNOWN_QUESTION'
  | 'COMPLETED';

export type LanguageMode = 'ne' | 'en' | 'auto';

export interface KnowledgeSource {
  id: string;
  title: string;
  document: string;
  page: number;
  section: string;
  excerpt: string;
  confidence: number;
  lastUpdated: string;
}

export interface AIActionResponse {
  answerEn: string;
  answerNe: string;
  intent: string;
  action: 'answer' | 'book_appointment' | 'create_ticket' | 'human_handoff' | 'department_redirect';
  sources: KnowledgeSource[];
  needsHuman?: boolean;
}

export interface TranscriptMessage {
  id: string;
  sender: 'user' | 'ai' | 'system';
  textEn: string;
  textNe: string;
  timestamp: string;
  sources?: KnowledgeSource[];
  intent?: string;
  actionType?: string;
}

export interface AppointmentData {
  department: string;
  targetPerson: string;
  date: string;
  timeSlot: string;
  visitorName: string;
  contact: string;
  purpose: string;
  referenceCode: string;
  createdAt: string;
}

export interface TicketData {
  ticketId: string;
  issueSummary: string;
  department: string;
  priority: 'Low' | 'Normal' | 'High';
  visitorName: string;
  contact: string;
  status: 'Open' | 'Assigned' | 'Resolved';
  createdAt: string;
}

export interface DepartmentInfo {
  id: string;
  name: string;
  nameNe: string;
  code: string;
  block: string;
  floor: string;
  room: string;
  hours: string;
  officer: string;
  contact: string;
}
