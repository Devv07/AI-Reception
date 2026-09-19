import {
  ConversationItem,
  VisitorRecord,
  AppointmentRecord,
  TicketRecord,
  KnowledgeDocument,
  AnalyticsData,
  OrganizationSettings,
  LiveEventItem,
} from '../types/dashboard';
import { KNOWLEDGE_SOURCES, DEPARTMENTS } from '../data/tcmitData';
import { DepartmentInfo } from '../types/reception';
import { demoStore } from './demoStore';
import { apiClient, BackendAppointment, BackendConversation, BackendDepartment, BackendTicket, BackendVisitor, getAccessToken } from './apiClient';

async function ensureDashboardAuth() {
  if (getAccessToken()) return;
  const email = import.meta.env.VITE_DASHBOARD_EMAIL;
  const password = import.meta.env.VITE_DASHBOARD_PASSWORD;
  if (!email || !password) {
    throw new Error('Dashboard credentials are not configured. Set VITE_DASHBOARD_EMAIL and VITE_DASHBOARD_PASSWORD.');
  }
  await apiClient.login(email, password);
}

function mapConversation(item: BackendConversation): ConversationItem {
  return {
    id: item.id,
    visitorId: item.visitor_id,
    visitorName: item.visitor_id,
    channel: item.channel === 'phone' ? 'Phone' : 'Reception',
    intent: item.messages.find((message) => message.intent)?.intent || 'general_information',
    startedAt: item.started_at,
    duration: 'Recorded session',
    status: item.status === 'human_requested' ? 'Human handoff' : item.status === 'active' ? 'Active' : 'Completed',
    language: 'en',
    messageCount: item.messages.length,
    sourcesUsed: [],
    actionTaken: item.status === 'human_requested' ? 'Human assistance requested' : undefined,
    messages: item.messages.map((message) => ({
      id: message.id,
      sender: message.role === 'assistant' ? 'AI' : 'USER',
      text: message.content,
      timestamp: message.created_at,
    })),
  };
}

function mapAppointment(item: BackendAppointment): AppointmentRecord {
  return {
    id: item.id,
    referenceCode: `APT-${item.id.slice(0, 8).toUpperCase()}`,
    visitorName: item.visitor_id,
    contact: '',
    targetPerson: item.requested_staff || 'Assigned staff',
    department: item.department_id,
    date: item.appointment_date,
    timeSlot: item.appointment_time,
    purpose: item.purpose,
    status: item.status === 'confirmed' ? 'Confirmed' : item.status === 'completed' ? 'Completed' : item.status === 'cancelled' ? 'Cancelled' : 'Pending',
    createdAt: item.created_at,
  };
}

function mapTicket(item: BackendTicket): TicketRecord {
  return {
    id: item.id,
    ticketId: `TCK-${item.id.slice(0, 8).toUpperCase()}`,
    issue: item.description,
    department: item.department_id,
    priority: item.priority === 'high' ? 'High' : item.priority === 'low' ? 'Low' : 'Normal',
    status: item.status === 'in_progress' ? 'In Progress' : item.status === 'resolved' || item.status === 'closed' ? 'Resolved' : 'Open',
    visitorName: item.visitor_id,
    contact: '',
    assignedStaff: item.assigned_user || 'Unassigned',
    createdAt: item.created_at,
  };
}

function mapDepartment(item: BackendDepartment): DepartmentInfo {
  return {
    id: item.id,
    name: item.name,
    nameNe: item.name,
    code: item.id.slice(0, 6).toUpperCase(),
    block: item.location || 'Main campus',
    floor: '',
    room: '',
    hours: '',
    officer: '',
    contact: item.contact || '',
  };
}

function mapVisitor(item: BackendVisitor): VisitorRecord {
  return {
    id: item.id,
    code: item.code,
    firstSeen: item.first_seen,
    lastInteraction: item.last_interaction,
    purpose: item.purpose,
    department: item.department,
    status: item.status,
    channel: item.channel,
    duration: item.duration,
  };
}

// Mock in-memory database for reactive dashboard actions
let MOCK_APPOINTMENTS: AppointmentRecord[] = [
  {
    id: 'apt-1',
    referenceCode: 'APT-1042',
    visitorName: 'Bikash Shrestha',
    contact: '9841234567',
    targetPerson: 'Prof. Dr. Rajendra Karki (Principal)',
    department: "Principal's Office",
    date: '2026-09-18',
    timeSlot: '11:00 AM',
    purpose: 'Academic Credit Transfer Consultation',
    status: 'Confirmed',
    createdAt: '10:14 AM',
  },
  {
    id: 'apt-2',
    referenceCode: 'APT-1043',
    visitorName: 'Pooja Thapa',
    contact: '9803112233',
    targetPerson: 'Mr. Sunil Sharma (Admissions Officer)',
    department: 'Admissions Office',
    date: '2026-09-18',
    timeSlot: '11:30 AM',
    purpose: 'BIT Fall Intake Document Verification',
    status: 'Pending',
    createdAt: '10:30 AM',
  },
  {
    id: 'apt-3',
    referenceCode: 'APT-1039',
    visitorName: 'Ramesh Adhikari',
    contact: '9812998877',
    targetPerson: 'Mrs. Sita Maharjan (Accounts Officer)',
    department: 'Accounts Section',
    date: '2026-09-18',
    timeSlot: '12:00 PM',
    purpose: 'Semester Installment Adjustment Discussion',
    status: 'Confirmed',
    createdAt: '09:45 AM',
  },
  {
    id: 'apt-4',
    referenceCode: 'APT-1028',
    visitorName: 'Aayush Koirala',
    contact: '9860123456',
    targetPerson: 'Er. Nabin Tamang (IT Head)',
    department: 'IT Department',
    date: '2026-09-19',
    timeSlot: '02:00 PM',
    purpose: 'Campus Network & Lab Access Credentials',
    status: 'Confirmed',
    createdAt: 'Yesterday',
  },
  {
    id: 'apt-5',
    referenceCode: 'APT-1011',
    visitorName: 'Nisha Gurung',
    contact: '9849556677',
    targetPerson: 'Prof. Dr. Rajendra Karki (Principal)',
    department: "Principal's Office",
    date: '2026-09-17',
    timeSlot: '10:30 AM',
    purpose: 'Scholarship Appeal Meeting',
    status: 'Completed',
    createdAt: '2 days ago',
  },
];

let MOCK_TICKETS: TicketRecord[] = [
  {
    id: 'tck-1',
    ticketId: 'TCK-2041',
    issue: 'Admission fee bank transfer not reflected on counter portal',
    department: 'Accounts Section',
    priority: 'High',
    status: 'Open',
    visitorName: 'Samir Thapa',
    contact: '9841882244',
    assignedStaff: 'Mrs. Sita Maharjan',
    createdAt: '10:28 AM',
  },
  {
    id: 'tck-2',
    ticketId: 'TCK-2039',
    issue: 'CMAT Entrance Scorecard discrepancy during registration',
    department: 'Admissions Office',
    priority: 'Normal',
    status: 'In Progress',
    visitorName: 'Anjali Sharma',
    contact: '9801456789',
    assignedStaff: 'Mr. Sunil Sharma',
    createdAt: '09:50 AM',
  },
  {
    id: 'tck-3',
    ticketId: 'TCK-2035',
    issue: 'Student portal password reset link expired',
    department: 'IT Department',
    priority: 'Low',
    status: 'Resolved',
    visitorName: 'Prashant Basnet',
    contact: '9813245678',
    assignedStaff: 'Er. Nabin Tamang',
    createdAt: 'Yesterday',
  },
  {
    id: 'tck-4',
    ticketId: 'TCK-2031',
    issue: 'Transfer certificate request for TU migration',
    department: 'Administration',
    priority: 'Normal',
    status: 'In Progress',
    visitorName: 'Kritika Joshi',
    contact: '9861239876',
    assignedStaff: 'Mr. Ramesh Bhatta',
    createdAt: 'Yesterday',
  },
  {
    id: 'tck-5',
    ticketId: 'TCK-2024',
    issue: 'Examination admit card printing error (Semester 3)',
    department: 'Examination Section',
    priority: 'High',
    status: 'Resolved',
    visitorName: 'Deepak Pandey',
    contact: '9840998811',
    assignedStaff: 'Mr. Hari Prasad Giri',
    createdAt: 'Sep 16, 2026',
  },
];

let MOCK_CONVERSATIONS: ConversationItem[] = [
  {
    id: 'cnv-101',
    visitorId: 'VIS-1042',
    visitorName: 'Samir Thapa',
    channel: 'Reception',
    intent: 'Payment Resolution / Support Ticket',
    startedAt: '10:26 AM',
    duration: '1m 45s',
    status: 'Completed',
    language: 'ne',
    messageCount: 4,
    sourcesUsed: [KNOWLEDGE_SOURCES.payment_policy],
    actionTaken: 'Created ticket TCK-2041 and notified Counter A-204',
    messages: [
      {
        id: 'm-1',
        sender: 'USER',
        text: 'मेरो admission payment ma समस्या भयो, पैसा काटियो तर receipt आएन।',
        timestamp: '10:26:15 AM',
      },
      {
        id: 'm-2',
        sender: 'AI',
        text: 'तपाईंको भर्ना शुल्क भुक्तानीमा समस्या देखिएकोमा क्षमाप्रार्थी छौं। म तुरुन्तै लेखा तथा भर्ना शाखाका लागि आधिकारिक Support Ticket दर्ता गरिदिन्छु, जसबाट काउन्टरमा सिधै समाधान हुनेछ।',
        timestamp: '10:26:18 AM',
        sources: [KNOWLEDGE_SOURCES.payment_policy],
      },
      {
        id: 'm-3',
        sender: 'SYSTEM',
        text: 'Service Ticket TCK-2041 dispatched to Accounts Section (Counter A-204). SMS confirmation sent.',
        timestamp: '10:27:02 AM',
      },
      {
        id: 'm-4',
        sender: 'AI',
        text: 'तपाईंको टिकट दर्ता भइसकेको छ। कृपया पहिलो तल्लाको कोठा A-204 मा जानुहोस्।',
        timestamp: '10:27:10 AM',
      },
    ],
  },
  {
    id: 'cnv-102',
    visitorId: 'VIS-1043',
    visitorName: 'Pooja Thapa',
    channel: 'Reception',
    intent: 'Admissions Inquiry (BIT)',
    startedAt: '10:30 AM',
    duration: '2m 10s',
    status: 'Completed',
    language: 'en',
    messageCount: 3,
    sourcesUsed: [KNOWLEDGE_SOURCES.bit_admission],
    actionTaken: 'Provided eligibility criteria and prospectus reference',
    messages: [
      {
        id: 'm-5',
        sender: 'USER',
        text: 'What are the eligibility requirements for the BIT program?',
        timestamp: '10:30:10 AM',
      },
      {
        id: 'm-6',
        sender: 'AI',
        text: 'For BIT admission at TCMIT, you need a minimum Grade C in all subjects of 10+2 / PCL with Mathematics or Computer Science. You also require your TU/CMAT entrance scorecard, character certificate, and academic mark sheets. Applications for the Fall 2026 intake are currently open at Counter A-102.',
        timestamp: '10:30:14 AM',
        sources: [KNOWLEDGE_SOURCES.bit_admission],
      },
      {
        id: 'm-7',
        sender: 'USER',
        text: 'Thank you! Where is Counter A-102 located?',
        timestamp: '10:31:00 AM',
      },
      {
        id: 'm-8',
        sender: 'AI',
        text: 'Counter A-102 is located right on the Ground Floor of Block A, just past the glass doors on your left.',
        timestamp: '10:31:05 AM',
      },
    ],
  },
  {
    id: 'cnv-103',
    visitorId: 'VIS-1044',
    visitorName: 'Rohan Shrestha',
    channel: 'Reception',
    intent: 'Direct Human Assistance',
    startedAt: '10:38 AM',
    duration: 'Active',
    status: 'Human handoff',
    language: 'ne',
    messageCount: 3,
    sourcesUsed: [],
    actionTaken: 'Dispatched notification to Counter A-102 duty officer',
    messages: [
      {
        id: 'm-9',
        sender: 'USER',
        text: 'मलाई भर्ना सम्बन्धी विशेष कुरा गर्न अफिसरलाई भेट्नु छ।',
        timestamp: '10:38:12 AM',
      },
      {
        id: 'm-10',
        sender: 'AI',
        text: 'म तपाईंलाई तुरुन्तै हाम्रो काउन्टर A-102 का ड्युटी अधिकृत श्री सुनील शर्मासँग जोड्दैछु।',
        timestamp: '10:38:15 AM',
      },
      {
        id: 'm-11',
        sender: 'STAFF',
        text: 'Mr. Sunil Sharma acknowledged alert from Kiosk. Visitor proceeding to Counter A-102.',
        timestamp: '10:39:00 AM',
      },
    ],
  },
  {
    id: 'cnv-104',
    visitorId: 'VIS-1038',
    visitorName: 'Anil Dangol',
    channel: 'Phone',
    intent: 'Campus Department Directory',
    startedAt: '09:40 AM',
    duration: '1m 15s',
    status: 'Completed',
    language: 'en',
    messageCount: 2,
    sourcesUsed: [],
    actionTaken: 'Gave Examination section operating hours and location',
    messages: [
      {
        id: 'm-12',
        sender: 'USER',
        text: 'What are the examination section opening hours today?',
        timestamp: '09:40:05 AM',
      },
      {
        id: 'm-13',
        sender: 'AI',
        text: 'The Examination Section in Block B (Room B-104) is open today from 8:00 AM to 4:00 PM. Officer Hari Prasad Giri is on duty.',
        timestamp: '09:40:08 AM',
      },
    ],
  },
];

let MOCK_VISITORS: VisitorRecord[] = [
  {
    id: 'vis-1',
    code: 'VIS-1044',
    firstSeen: '10:38 AM',
    lastInteraction: 'Just now',
    purpose: 'Front Desk Consultation',
    department: 'Admissions Office',
    status: 'Needs staff',
    channel: 'Reception Kiosk',
    duration: '2m',
  },
  {
    id: 'vis-2',
    code: 'VIS-1043',
    firstSeen: '10:30 AM',
    lastInteraction: '10:32 AM',
    purpose: 'BIT Admissions Info',
    department: 'Admissions Office',
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '2m 10s',
  },
  {
    id: 'vis-3',
    code: 'VIS-1042',
    firstSeen: '10:26 AM',
    lastInteraction: '10:28 AM',
    purpose: 'Fee Payment Ticket',
    department: 'Accounts Section',
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '1m 45s',
  },
  {
    id: 'vis-4',
    code: 'VIS-1041',
    firstSeen: '10:10 AM',
    lastInteraction: '10:14 AM',
    purpose: "Principal's Office Appointment",
    department: "Principal's Office",
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '4m 00s',
  },
  {
    id: 'vis-5',
    code: 'VIS-1040',
    firstSeen: '09:55 AM',
    lastInteraction: '09:58 AM',
    purpose: 'Lab Credentials Check',
    department: 'IT Department',
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '3m 12s',
  },
  {
    id: 'vis-6',
    code: 'VIS-1039',
    firstSeen: '09:42 AM',
    lastInteraction: '09:45 AM',
    purpose: 'Transcript Inquiry',
    department: 'Examination Section',
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '1m 50s',
  },
  {
    id: 'vis-7',
    code: 'VIS-1038',
    firstSeen: '09:40 AM',
    lastInteraction: '09:41 AM',
    purpose: 'Exam Hours Phone Inquiry',
    department: 'Examination Section',
    status: 'Completed',
    channel: 'Phone Call',
    duration: '1m 15s',
  },
  {
    id: 'vis-8',
    code: 'VIS-1037',
    firstSeen: '09:15 AM',
    lastInteraction: '09:20 AM',
    purpose: 'Campus Tour & Wayfinding',
    department: 'Administration',
    status: 'Completed',
    channel: 'Reception Kiosk',
    duration: '5m',
  },
];

let MOCK_KNOWLEDGE_DOCUMENTS: KnowledgeDocument[] = [
  {
    id: 'doc-1',
    name: 'TCMIT Undergraduate Admissions Prospectus 2026.pdf',
    size: '4.8 MB',
    pages: 28,
    status: 'Indexed',
    uploadedAt: 'Sep 10, 2026',
    lastIndexed: '2 hours ago',
    department: 'Admissions Office',
  },
  {
    id: 'doc-2',
    name: 'Executive Protocol & Principal Visitor Guidelines.pdf',
    size: '1.2 MB',
    pages: 8,
    status: 'Indexed',
    uploadedAt: 'Sep 05, 2026',
    lastIndexed: 'Yesterday',
    department: "Principal's Office",
  },
  {
    id: 'doc-3',
    name: 'Student Accounts, Fee Structures & Refund Policies.pdf',
    size: '2.4 MB',
    pages: 14,
    status: 'Indexed',
    uploadedAt: 'Aug 28, 2026',
    lastIndexed: '3 days ago',
    department: 'Accounts Section',
  },
  {
    id: 'doc-4',
    name: 'TCMIT Academic Calendar & Examination Rules Fall 2026.pdf',
    size: '3.1 MB',
    pages: 20,
    status: 'Indexed',
    uploadedAt: 'Sep 12, 2026',
    lastIndexed: 'Sep 14, 2026',
    department: 'Examination Section',
  },
  {
    id: 'doc-5',
    name: 'Campus IT Infrastructure & Lab Policy 2026.pdf',
    size: '1.9 MB',
    pages: 12,
    status: 'Indexed',
    uploadedAt: 'Sep 01, 2026',
    lastIndexed: 'Sep 02, 2026',
    department: 'IT Department',
  },
];

let MOCK_SETTINGS: OrganizationSettings = {
  name: 'Tribhuvan College of Management & IT',
  code: 'TCMIT-KTM',
  address: 'Tinkune, Subidhanagar, Kathmandu, Nepal',
  contactPhone: '+977-1-4112233',
  contactEmail: 'reception@tcmit.edu.np',
  operatingHours: 'Sun - Fri: 7:00 AM - 5:00 PM (Sat Closed)',
  kioskId: 'KIOSK-LOBBY-01',
  greetingEn: "Namaste. Welcome to TCMIT. I'm your AI receptionist. How can I help you today?",
  greetingNe: 'नमस्ते, TCMIT मा स्वागत छ। म यहाँको AI रिसेप्सनिस्ट हुँ। म तपाईंलाई कसरी सहयोग गर्न सक्छु?',
  fallbackResponse: "I don't have enough verified information to answer that confidently. I can connect you with a staff member.",
  handoffDutyDesk: 'Counter A-102 (Admissions & Front Desk)',
  cameraDetectionEnabled: true,
  privacyMode: true,
  speechRate: 0.95,
};

let MOCK_LIVE_EVENTS: LiveEventItem[] = [
  {
    id: 'ev-1',
    time: '10:38:12',
    type: 'visitor_detected',
    description: 'Visitor approached Kiosk A-01 (Proximity: 1.2m)',
  },
  {
    id: 'ev-2',
    time: '10:38:13',
    type: 'session_started',
    description: 'Bilingual session initiated (Devanagari UI active)',
  },
  {
    id: 'ev-3',
    time: '10:38:15',
    type: 'transcript',
    description: 'User input captured: "मलाई भर्ना सम्बन्धी विशेष कुरा गर्न अफिसरलाई भेट्नु छ।"',
  },
  {
    id: 'ev-4',
    time: '10:38:16',
    type: 'intent_classified',
    description: 'Intent resolved: Direct Human Assistance (Confidence: 99.4%)',
  },
  {
    id: 'ev-5',
    time: '10:38:18',
    type: 'handoff_requested',
    description: 'Human handoff triggered → Front Desk Counter A-102 terminal notified',
  },
  {
    id: 'ev-6',
    time: '10:30:10',
    type: 'visitor_detected',
    description: 'Visitor session started (VIS-1043)',
  },
  {
    id: 'ev-7',
    time: '10:30:14',
    type: 'source_retrieved',
    description: 'Retrieved "TCMIT Undergraduate Admissions Prospectus 2026.pdf" (Page 2)',
  },
  {
    id: 'ev-8',
    time: '10:30:16',
    type: 'answer_delivered',
    description: 'TTS response synthesized and played (Duration: 9.4s)',
  },
  {
    id: 'ev-9',
    time: '10:26:18',
    type: 'ticket_created',
    description: 'Generated Priority Support Ticket TCK-2041 for Accounts Section',
  },
  {
    id: 'ev-10',
    time: '10:14:22',
    type: 'appointment_booked',
    description: "Confirmed Appointment APT-1042 for Principal's Office",
  },
];

export class DashboardService {
  /**
   * Returns high-level overview metrics for the operational control center.
   */
  static async getOverviewMetrics() {
    await ensureDashboardAuth();
    const [visitors, conversations, appointments, tickets] = await Promise.all([
      apiClient.listVisitors(),
      apiClient.listConversations(),
      apiClient.listAppointments(),
      apiClient.listTickets(),
    ]);
    const today = new Date().toISOString().slice(0, 10);
    const todayApts = appointments.filter((item) => item.appointment_date === today);
    const openTcks = tickets.filter((item) => !['resolved', 'closed'].includes(item.status));
    const handoffsCount = conversations.filter((item) => item.status === 'human_requested').length;

    return {
      todayVisitors: {
        title: "Today's Visitors",
        value: visitors.length,
        change: 'Persisted visitor records',
        trend: 'up' as const,
        subtext: '88% handled autonomously by AI',
      },
      conversations: {
        title: 'AI Conversations',
        value: conversations.length,
        change: 'Persisted conversation records',
        trend: 'up' as const,
        subtext: 'Average duration 1m 58s',
      },
      appointments: {
        title: 'Appointments Today',
        value: todayApts.length,
        change: `${todayApts.filter((a) => a.status === 'confirmed').length} confirmed, ${todayApts.filter((a) => a.status === 'pending').length} pending`,
        trend: 'neutral' as const,
        subtext: 'Synchronized live with Reception Kiosk',
      },
      openTickets: {
        title: 'Open Support Tickets',
        value: openTcks.length,
        change: `${openTcks.filter((t) => t.priority === 'high').length} High priority`,
        trend: 'down' as const,
        subtext: 'Auto-dispatched by AI Receptionist',
      },
      handoffs: {
        title: 'Human Handoffs',
        value: Math.max(handoffsCount, 3),
        change: handoffsCount ? `${handoffsCount} conversations awaiting staff` : 'No pending handoffs',
        trend: (handoffsCount ? 'up' : 'neutral') as 'up' | 'neutral' | 'down',
        subtext: 'Persisted conversation status',
      },
    };
  }

  /**
   * Returns live reception status for /dashboard/live.
   */
  static async getLiveReceptionState() {
    await new Promise((r) => setTimeout(r, 100));
    const s = demoStore.getState();
    return {
      kioskStatus: 'Online',
      kioskId: 'KIOSK-LOBBY-01',
      cameraActive: s.sensorActive,
      lastPing: `Just now (${new Date().toLocaleTimeString()})`,
      currentVisitor: s.currentVisitor,
      currentAiState: s.receptionState,
      currentIntent:
        s.intent || (s.receptionState === 'HANDOFF' ? 'Direct Human Assistance' : 'Campus Assistance'),
      confidence: s.confidence || (s.sources.length > 0 ? s.sources[0].confidence : 0.98),
      retrievedSource: s.sources.length > 0 ? s.sources[0] : null,
      activeAction:
        s.activeAction ||
        (s.receptionState === 'IDLE' ? 'Awaiting visitor interaction' : 'Processing interaction'),
      currentConversation: s.conversations.find((c) => c.id === 'cnv-101') || s.conversations[0],
      liveEvents: [...s.liveEvents],
      handoffAlert: s.handoffAlert || {
        isActive: false,
        reason: '',
        visitorCode: '',
        counter: '',
        dutyOfficer: '',
        time: '',
      },
    };
  }

  /**
   * Acknowledge or dismiss a live handoff alert.
   */
  static async acknowledgeHandoff(notes?: string) {
    await new Promise((r) => setTimeout(r, 150));
    demoStore.acknowledgeHandoff(notes);
    return { success: true };
  }

  /**
   * Fetch conversations list with optional search and filter.
   */
  static async getConversations(search?: string, channelFilter?: string) {
    await ensureDashboardAuth();
    let items = (await apiClient.listConversations()).map(mapConversation);
    if (channelFilter && channelFilter !== 'all') {
      items = items.filter((c) => c.channel.toLowerCase() === channelFilter.toLowerCase());
    }
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(
        (c) =>
          c.intent.toLowerCase().includes(q) ||
          c.visitorName?.toLowerCase().includes(q) ||
          c.visitorId.toLowerCase().includes(q) ||
          c.messages.some((m) => m.text.toLowerCase().includes(q))
      );
    }
    return items;
  }

  /**
   * Fetch specific conversation detail.
   */
  static async getConversationDetail(id: string) {
    await ensureDashboardAuth();
    return mapConversation(await apiClient.getConversation(id));
  }

  /**
   * Fetch visitors record list.
   */
  static async getVisitors(search?: string, statusFilter?: string) {
    await ensureDashboardAuth();
    let items = (await apiClient.listVisitors()).map(mapVisitor);
    if (statusFilter && statusFilter !== 'all') {
      items = items.filter((v) => v.status.toLowerCase() === statusFilter.toLowerCase());
    }
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(
        (v) =>
          v.code.toLowerCase().includes(q) ||
          v.purpose.toLowerCase().includes(q) ||
          v.department.toLowerCase().includes(q)
      );
    }
    return items;
  }

  /**
   * Fetch appointments with date filtering.
   */
  static async getAppointments(filter?: string) {
    await ensureDashboardAuth();
    let items = (await apiClient.listAppointments()).map(mapAppointment);
    if (filter && filter !== 'all') {
      items = items.filter((a) => a.status.toLowerCase() === filter.toLowerCase());
    }
    return items;
  }

  /**
   * Update appointment status.
   */
  static async updateAppointmentStatus(id: string, status: AppointmentRecord['status']) {
    await ensureDashboardAuth();
    return mapAppointment(await apiClient.updateAppointment(id, status));
  }

  /**
   * Fetch tickets list.
   */
  static async getTickets(filter?: string) {
    await ensureDashboardAuth();
    let items = (await apiClient.listTickets()).map(mapTicket);
    if (filter && filter !== 'all') {
      items = items.filter((t) => t.status.toLowerCase() === filter.toLowerCase());
    }
    return items;
  }

  /**
   * Update ticket status.
   */
  static async updateTicketStatus(id: string, status: TicketRecord['status']) {
    await ensureDashboardAuth();
    return mapTicket(await apiClient.updateTicket(id, status));
  }

  /**
   * Fetch knowledge documents.
   */
  static async getKnowledgeDocuments() {
    await new Promise((r) => setTimeout(r, 350));
    return [...MOCK_KNOWLEDGE_DOCUMENTS];
  }

  /**
   * Test knowledge base query search (RAG Sandbox).
   */
  static async testKnowledgeSearch(query: string) {
    await new Promise((r) => setTimeout(r, 500));
    const q = query.toLowerCase();
    if (q.includes('admission') || q.includes('bit') || q.includes('grade')) {
      return {
        matched: true,
        source: KNOWLEDGE_SOURCES.bit_admission,
        score: 0.98,
        retrievedParagraph:
          'Undergraduate BIT eligibility requires a minimum Grade C in all subjects of 10+2 / PCL with Mathematics or Computer Science. Entrance TU/CMAT scorecard is mandatory for Fall 2026 registration.',
      };
    }
    if (q.includes('fee') || q.includes('payment') || q.includes('refund')) {
      return {
        matched: true,
        source: KNOWLEDGE_SOURCES.payment_policy,
        score: 0.94,
        retrievedParagraph:
          'Payment verification issues should be logged via front-desk ticketing. Bank vouchers must match the registered applicant TU roll number.',
      };
    }
    if (q.includes('principal') || q.includes('appointment')) {
      return {
        matched: true,
        source: KNOWLEDGE_SOURCES.principal_policy,
        score: 0.96,
        retrievedParagraph:
          "Principal Prof. Dr. Rajendra Karki meets visitors between 10:00 AM and 1:30 PM by prior appointment in Block B-201.",
      };
    }
    return {
      matched: false,
      source: null,
      score: 0.32,
      retrievedParagraph: 'No confident match in verified institutional corpus.',
    };
  }

  /**
   * Add a new document to knowledge base.
   */
  static async uploadDocument(name: string, size: string, department: string) {
    await new Promise((r) => setTimeout(r, 600));
    const newDoc: KnowledgeDocument = {
      id: `doc-${Date.now()}`,
      name,
      size,
      pages: Math.floor(Math.random() * 20 + 5),
      status: 'Indexed',
      uploadedAt: 'Just now',
      lastIndexed: 'Just now',
      department,
    };
    MOCK_KNOWLEDGE_DOCUMENTS.unshift(newDoc);
    return newDoc;
  }

  /**
   * Fetch departments.
   */
  static async getDepartments(): Promise<DepartmentInfo[]> {
    await ensureDashboardAuth();
    return (await apiClient.listDepartments()).map(mapDepartment);
  }

  /**
   * Fetch analytics data for charts.
   */
  static async getAnalyticsData(timeframe = 'today'): Promise<AnalyticsData> {
    await ensureDashboardAuth();
    const data = await apiClient.getAnalytics(timeframe);
    return {
      visitorsByHour: data.visitors_by_hour,
      topIntents: data.top_intents,
      departmentDemand: data.department_demand,
      channelUsage: data.channel_usage,
      outcomes: data.outcomes,
    };
  }

  /**
   * Fetch settings.
   */
  static async getSettings(): Promise<OrganizationSettings> {
    await new Promise((r) => setTimeout(r, 300));
    return { ...MOCK_SETTINGS };
  }

  /**
   * Save settings.
   */
  static async updateSettings(settings: Partial<OrganizationSettings>) {
    await new Promise((r) => setTimeout(r, 400));
    MOCK_SETTINGS = { ...MOCK_SETTINGS, ...settings };
    return { ...MOCK_SETTINGS };
  }
}
