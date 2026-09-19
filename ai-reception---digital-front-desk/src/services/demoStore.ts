import { useState, useEffect } from 'react';
import {
  ReceptionState,
  LanguageMode,
  KnowledgeSource,
  AppointmentData,
  TicketData,
} from '../types/reception';
import {
  AppointmentRecord,
  TicketRecord,
  VisitorRecord,
  ConversationItem,
  LiveEventItem,
} from '../types/dashboard';
import { KNOWLEDGE_SOURCES } from '../data/tcmitData';
import { ReceptionService } from './receptionService';

export interface DemoStepInfo {
  step: number;
  title: string;
  description: string;
  badge: string;
}

export const DEMO_STEPS: DemoStepInfo[] = [
  {
    step: 1,
    title: 'Visitor detected',
    description: 'Proximity radar trips at Kiosk A-01 (1.1m). Visual indicator highlights visitor presence.',
    badge: 'Hardware Sensor',
  },
  {
    step: 2,
    title: 'Reception wakes',
    description: 'Kiosk screen wakes from ambient idle into active greeting state. Welcoming voice prompt ready.',
    badge: 'Kiosk Wake',
  },
  {
    step: 3,
    title: 'Conversation begins',
    description: 'Microphone array activates listening state with real-time audio waveform visualizer.',
    badge: 'Speech Input',
  },
  {
    step: 4,
    title: 'Visitor asks Nepali admission question',
    description: 'Visitor speaks in Nepali: "मलाई BIT admission को लागि के के चाहिन्छ?" Intent classified.',
    badge: 'Nepali NLU',
  },
  {
    step: 5,
    title: 'AI responds',
    description: 'AI synthesizes verified response in natural Nepali and speaks through kiosk speakers.',
    badge: 'Voice Synthesis',
  },
  {
    step: 6,
    title: 'Knowledge source appears',
    description: 'Grounding evidence card surfaces verified excerpt from Admissions Prospectus 2026.',
    badge: 'RAG Evidence',
  },
  {
    step: 7,
    title: 'Visitor requests appointment',
    description: 'Visitor requests executive meeting with Principal. Calendar booking interface appears.',
    badge: 'Appointment Flow',
  },
  {
    step: 8,
    title: 'Appointment is booked',
    description: 'Appointment APT-1045 confirmed. Instantly appears on Admin Dashboard in real time.',
    badge: 'Real-time Sync',
  },
  {
    step: 9,
    title: 'Visitor reports payment issue',
    description: 'Visitor reports bank transaction anomaly. AI routes to Support Ticket generation modal.',
    badge: 'Support Issue',
  },
  {
    step: 10,
    title: 'Ticket is created',
    description: 'Priority ticket TCK-2045 generated for Accounts Section. Dashboard ticket count updates.',
    badge: 'Escalation',
  },
  {
    step: 11,
    title: 'Human handoff requested',
    description: 'Visitor requests human staff. Red alert flashes on Admin Live Operations center.',
    badge: 'Human Handoff',
  },
  {
    step: 12,
    title: 'Admin dashboard updates in real time',
    description: 'Staff terminal acknowledges handoff alert at Counter A-102. Full cycle completed.',
    badge: 'Complete Cycle',
  },
];

export interface DemoState {
  // Kiosk View State
  receptionState: ReceptionState;
  language: LanguageMode;
  audioEnabled: boolean;
  sensorActive: boolean;
  userQuery: string | null;
  aiResponse: { en: string; ne: string } | null;
  sources: KnowledgeSource[];
  intent?: string;
  confidence?: number;
  activeAppointment: AppointmentData | null;
  activeTicket: TicketData | null;
  isDirectoryOpen: boolean;
  isTextDrawerOpen: boolean;

  // Live Telemetry
  currentVisitor: {
    code: string;
    name: string;
    status: 'Active' | 'Completed' | 'Needs staff';
    arrival: string;
    waitingDuration: string;
    currentLocation: string;
  } | null;

  activeAction: string | null;
  handoffAlert: {
    isActive: boolean;
    reason: string;
    visitorCode: string;
    counter: string;
    dutyOfficer: string;
    time: string;
  } | null;

  // Shared Collections
  appointments: AppointmentRecord[];
  tickets: TicketRecord[];
  visitors: VisitorRecord[];
  conversations: ConversationItem[];
  liveEvents: LiveEventItem[];

  // Demo Simulator Controls
  currentStep: number;
  isPlaying: boolean;
  speed: 'normal' | 'fast' | 'slow';
  stepTitle: string;
  stepDescription: string;
}

const INITIAL_APPOINTMENTS: AppointmentRecord[] = [
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

const INITIAL_TICKETS: TicketRecord[] = [
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

const INITIAL_VISITORS: VisitorRecord[] = [
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

const INITIAL_CONVERSATIONS: ConversationItem[] = [
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
];

const INITIAL_LIVE_EVENTS: LiveEventItem[] = [
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

function createInitialState(): DemoState {
  return {
    receptionState: 'IDLE',
    language: 'en',
    audioEnabled: true,
    sensorActive: false,
    userQuery: null,
    aiResponse: null,
    sources: [],
    intent: undefined,
    confidence: undefined,
    activeAppointment: null,
    activeTicket: null,
    isDirectoryOpen: false,
    isTextDrawerOpen: false,

    currentVisitor: {
      code: 'VIS-1045',
      name: 'Aarav Sharma',
      status: 'Active',
      arrival: '10:45 AM',
      waitingDuration: 'Just now',
      currentLocation: 'Kiosk Front Desk A-01',
    },

    activeAction: 'Ready for visitor query',
    handoffAlert: null,

    appointments: [...INITIAL_APPOINTMENTS],
    tickets: [...INITIAL_TICKETS],
    visitors: [...INITIAL_VISITORS],
    conversations: [...INITIAL_CONVERSATIONS],
    liveEvents: [...INITIAL_LIVE_EVENTS],

    currentStep: 0,
    isPlaying: false,
    speed: 'normal',
    stepTitle: 'Idle Ready',
    stepDescription: 'AI Reception Kiosk is running in ambient standby mode waiting for a visitor.',
  };
}

class DemoStoreClass {
  private state: DemoState = createInitialState();
  private listeners: Set<() => void> = new Set();
  private timer: any = null;

  getState(): DemoState {
    return this.state;
  }

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    this.listeners.forEach((listener) => {
      try {
        listener();
      } catch (e) {
        console.error('DemoStore listener error:', e);
      }
    });
  }

  setState(partial: Partial<DemoState> | ((prev: DemoState) => Partial<DemoState>)) {
    const patch = typeof partial === 'function' ? partial(this.state) : partial;
    this.state = { ...this.state, ...patch };
    this.notify();
  }

  // Reset all state to clean initial
  resetDemo() {
    this.pauseAutoPlay();
    this.state = createInitialState();
    this.notify();
  }

  resetToIdle() {
    this.pauseAutoPlay();
    this.setState({
      receptionState: 'IDLE',
      userQuery: null,
      aiResponse: null,
      sources: [],
      intent: undefined,
      confidence: undefined,
      activeAppointment: null,
      activeTicket: null,
      sensorActive: false,
      isDirectoryOpen: false,
      isTextDrawerOpen: false,
      currentStep: 0,
      stepTitle: 'Idle Ready',
      stepDescription: 'Kiosk returned to ambient idle waiting for visitors.',
    });
  }

  // Log a live event into the stream (which both dashboard and reception show)
  logLiveEvent(type: LiveEventItem['type'], description: string) {
    const newEvent: LiveEventItem = {
      id: `ev-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      time: new Date().toLocaleTimeString(),
      type,
      description,
    };
    this.setState((prev) => ({
      liveEvents: [newEvent, ...prev.liveEvents],
    }));
  }

  // ==========================================
  // 12-STEP SIMULATION ENGINE
  // ==========================================
  executeStep(stepNum: number) {
    if (stepNum < 1 || stepNum > 12) return;

    const stepDef = DEMO_STEPS.find((s) => s.step === stepNum)!;
    const nowTime = new Date().toLocaleTimeString();

    switch (stepNum) {
      case 1: {
        // 1. Visitor detected
        ReceptionService.playChime('wake');
        this.setState((prev) => {
          const visitorRecord: VisitorRecord = {
            id: 'vis-1045',
            code: 'VIS-1045',
            firstSeen: nowTime,
            lastInteraction: 'Just arrived',
            purpose: 'BIT Admissions & Scholarship Inquiry',
            department: 'Admissions Office',
            status: 'Active',
            channel: 'Reception Kiosk',
            duration: '0m',
          };
          const exists = prev.visitors.some((v) => v.code === 'VIS-1045');
          return {
            currentStep: 1,
            stepTitle: stepDef.title,
            stepDescription: stepDef.description,
            receptionState: 'VISITOR_DETECTED',
            sensorActive: true,
            userQuery: null,
            aiResponse: null,
            sources: [],
            intent: 'Visitor Approached',
            activeAction: 'Presence sensor triggered · Screen lighting activated',
            currentVisitor: {
              code: 'VIS-1045',
              name: 'Aarav Sharma',
              status: 'Active',
              arrival: nowTime,
              waitingDuration: '0m',
              currentLocation: 'Kiosk Front Desk A-01',
            },
            visitors: exists ? prev.visitors : [visitorRecord, ...prev.visitors],
          };
        });
        this.logLiveEvent('visitor_detected', 'Visitor approached Kiosk A-01 (Proximity radar: 1.1m)');
        break;
      }

      case 2: {
        // 2. Reception wakes
        ReceptionService.playChime('wake');
        this.setState({
          currentStep: 2,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'IDLE',
          sensorActive: true,
          userQuery: null,
          aiResponse: null,
          sources: [],
          intent: 'Greeting Standby',
          activeAction: 'Front desk touch and voice interaction initialized',
        });
        this.logLiveEvent('session_started', 'Kiosk screen awakened from ambient idle. Reception UI ready for interaction.');
        break;
      }

      case 3: {
        // 3. Conversation begins
        this.setState({
          currentStep: 3,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'LISTENING',
          sensorActive: true,
          userQuery: this.state.language === 'ne' ? 'आवाज सुन्दैछ...' : 'Listening to voice...',
          aiResponse: null,
          sources: [],
          intent: 'Voice Capture',
          activeAction: 'Dual-microphone array active · Listening for visitor query',
        });
        this.logLiveEvent('listening', 'Audio input stream open. Dual microphone array active.');
        break;
      }

      case 4: {
        // 4. Visitor asks Nepali admission question
        this.setState({
          currentStep: 4,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'THINKING',
          language: 'ne',
          userQuery: 'मलाई BIT admission को लागि के के चाहिन्छ?',
          intent: 'Admissions Inquiry (BIT)',
          confidence: 0.991,
          activeAction: 'Natural language analysis & RAG knowledge retrieval',
        });
        this.logLiveEvent('transcript', 'User input captured (Nepali): "मलाई BIT admission को लागि के के चाहिन्छ?"');
        this.logLiveEvent('intent_classified', 'Intent resolved: Admissions Inquiry (BIT) [Confidence: 99.1%]');
        break;
      }

      case 5: {
        // 5. AI responds
        const answerNe =
          'TCMIT मा BIT भर्नाका लागि कक्षा १२ वा प्रवीणता प्रमाणपत्र तहमा कम्तीमा Grade C ल्याएको हुनुपर्छ (गणित वा कम्प्युटर साइन्स अनिवार्य)। साथै TU प्रवेश परीक्षाको Scorecard, ट्रान्सक्रिप्ट र चारित्रिक प्रमाणपत्र आवश्यक पर्दछ। भर्ना फारम काउन्टर A-102 मा उपलब्ध छ।';
        const answerEn =
          'For BIT admission at TCMIT, you need a minimum Grade C in all subjects of 10+2 / PCL with Mathematics or Computer Science. You also require your TU/CMAT entrance scorecard, character certificate, and academic mark sheets. Applications for the Fall 2026 intake are currently open at Counter A-102.';

        this.setState({
          currentStep: 5,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'SPEAKING',
          aiResponse: { en: answerEn, ne: answerNe },
          intent: 'Admissions Inquiry (BIT)',
          confidence: 0.991,
          activeAction: 'Synthesizing Nepali speech response and playing audio',
        });

        if (this.state.audioEnabled) {
          ReceptionService.speak(answerNe, 'ne');
        }
        this.logLiveEvent('answer_delivered', 'TTS voice response synthesized and played (Audio duration: ~8.2s)');
        break;
      }

      case 6: {
        // 6. Knowledge source appears
        const source = KNOWLEDGE_SOURCES.bit_admission;
        this.setState({
          currentStep: 6,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'COMPLETED',
          sources: [source],
          activeAction: 'Surfaced verified grounding excerpt from Admissions Prospectus 2026',
        });
        this.logLiveEvent('source_retrieved', 'Grounding evidence verified: "TCMIT Undergraduate Admissions Prospectus 2026.pdf" (Clause 3.1, Page 2, Confidence 98%)');
        break;
      }

      case 7: {
        // 7. Visitor requests appointment
        this.setState({
          currentStep: 7,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'ACTION_APPOINTMENT',
          userQuery: 'Principal लाई भेट्न appointment लिन मिल्छ?',
          intent: "Executive Consultation (Principal's Office)",
          confidence: 0.994,
          activeAction: 'Opened interactive appointment booking module for Room B-201',
        });
        this.logLiveEvent('transcript', 'Visitor query: "Principal लाई भेट्न appointment लिन मिल्छ?"');
        this.logLiveEvent('intent_classified', "Intent resolved: Executive Consultation (Principal's Office) [Confidence: 99.4%]");
        break;
      }

      case 8: {
        // 8. Appointment is booked
        ReceptionService.playChime('success');
        const newAptData: AppointmentData = {
          referenceCode: 'APT-1045',
          visitorName: 'Aarav Sharma',
          contact: '9841223344',
          targetPerson: 'Prof. Dr. Rajendra Karki (Principal)',
          department: "Principal's Office",
          date: '2026-09-18',
          timeSlot: '11:45 AM',
          purpose: 'BIT Special Scholarship & Credit Consultation',
          createdAt: nowTime,
        };

        const newAptRecord: AppointmentRecord = {
          id: 'apt-1045',
          referenceCode: 'APT-1045',
          visitorName: 'Aarav Sharma',
          contact: '9841223344',
          targetPerson: 'Prof. Dr. Rajendra Karki (Principal)',
          department: "Principal's Office",
          date: '2026-09-18',
          timeSlot: '11:45 AM',
          purpose: 'BIT Special Scholarship & Credit Consultation',
          status: 'Confirmed',
          createdAt: nowTime,
        };

        this.setState((prev) => ({
          currentStep: 8,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'COMPLETED',
          activeAppointment: newAptData,
          appointments: [newAptRecord, ...prev.appointments.filter((a) => a.id !== 'apt-1045')],
          activeAction: 'Appointment APT-1045 confirmed and synchronized with Executive Calendar',
        }));

        this.logLiveEvent('appointment_booked', "Confirmed Appointment APT-1045 for Principal's Office (Aarav Sharma - 11:45 AM)");
        break;
      }

      case 9: {
        // 9. Visitor reports payment issue
        this.setState({
          currentStep: 9,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'ACTION_TICKET',
          activeAppointment: null,
          userQuery: 'मेरो admission payment मा समस्या भयो, पैसा काटियो तर receipt आएन।',
          intent: 'Payment Resolution / Support Ticket',
          confidence: 0.988,
          activeAction: 'Opened priority ticket generation interface for Accounts Section',
        });
        this.logLiveEvent('transcript', 'Visitor query: "मेरो admission payment मा समस्या भयो, पैसा काटियो तर receipt आएन।"');
        this.logLiveEvent('intent_classified', 'Intent resolved: Payment Resolution / Support Ticket [Confidence: 98.8%]');
        break;
      }

      case 10: {
        // 10. Ticket is created
        ReceptionService.playChime('success');
        const newTicketData: TicketData = {
          ticketId: 'TCK-2045',
          issueSummary: 'Bank admission payment debited but counter receipt missing',
          department: 'Accounts Section',
          priority: 'High',
          visitorName: 'Aarav Sharma',
          contact: '9841223344',
          status: 'Open',
          createdAt: nowTime,
        };

        const newTicketRecord: TicketRecord = {
          id: 'tck-2045',
          ticketId: 'TCK-2045',
          issue: 'Bank admission payment debited but counter receipt missing',
          department: 'Accounts Section',
          priority: 'High',
          status: 'Open',
          visitorName: 'Aarav Sharma',
          contact: '9841223344',
          assignedStaff: 'Mrs. Sita Maharjan',
          createdAt: nowTime,
        };

        this.setState((prev) => ({
          currentStep: 10,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'COMPLETED',
          activeTicket: newTicketData,
          tickets: [newTicketRecord, ...prev.tickets.filter((t) => t.id !== 'tck-2045')],
          activeAction: 'Generated Priority Ticket TCK-2045 dispatched to Accounts Section (Counter A-204)',
        }));

        this.logLiveEvent('ticket_created', 'Generated Priority Support Ticket TCK-2045 for Accounts Section (Counter A-204)');
        break;
      }

      case 11: {
        // 11. Human handoff requested
        ReceptionService.playChime('alert');
        this.setState((prev) => ({
          currentStep: 11,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          receptionState: 'HANDOFF',
          activeTicket: null,
          activeAppointment: null,
          userQuery: 'मलाई काउन्टर अधिकृतसँग प्रत्यक्ष कुरा गर्नु छ।',
          intent: 'Direct Human Assistance',
          confidence: 0.996,
          activeAction: 'Dispatched urgent visitor handoff notification to Counter A-102 terminal',
          currentVisitor: prev.currentVisitor
            ? { ...prev.currentVisitor, status: 'Needs staff' }
            : null,
          handoffAlert: {
            isActive: true,
            reason: 'Visitor requested in-person admission counseling with front desk duty officer',
            visitorCode: 'VIS-1045',
            counter: 'Counter A-102',
            dutyOfficer: 'Mr. Sunil Sharma',
            time: nowTime,
          },
          visitors: prev.visitors.map((v) =>
            v.code === 'VIS-1045' ? { ...v, status: 'Needs staff' } : v
          ),
        }));

        this.logLiveEvent('handoff_requested', 'Human handoff triggered → Front Desk Counter A-102 terminal notified');
        break;
      }

      case 12: {
        // 12. Admin dashboard updates in real time
        this.setState((prev) => ({
          currentStep: 12,
          stepTitle: stepDef.title,
          stepDescription: stepDef.description,
          activeAction: 'Duty Officer Mr. Sunil Sharma acknowledged handoff alert. Full cycle synchronized across kiosk and admin.',
          handoffAlert: prev.handoffAlert ? { ...prev.handoffAlert, isActive: false } : null,
          currentVisitor: prev.currentVisitor
            ? { ...prev.currentVisitor, status: 'Completed' }
            : null,
          visitors: prev.visitors.map((v) =>
            v.code === 'VIS-1045' ? { ...v, status: 'Completed' } : v
          ),
        }));

        this.logLiveEvent('session_ended', 'Duty Officer Mr. Sunil Sharma acknowledged handoff. Visitor guided to Counter A-102.');
        break;
      }
    }
  }

  // Advance to next step
  nextStep() {
    const next = this.state.currentStep >= 12 ? 1 : this.state.currentStep + 1;
    this.executeStep(next);
  }

  // Go to previous step
  prevStep() {
    const prev = this.state.currentStep <= 1 ? 12 : this.state.currentStep - 1;
    this.executeStep(prev);
  }

  // Auto-play the 12 steps
  startAutoPlay() {
    this.pauseAutoPlay();
    this.setState({ isPlaying: true });

    // If at 0 or 12, restart from 1
    if (this.state.currentStep === 0 || this.state.currentStep >= 12) {
      this.executeStep(1);
    }

    const intervalMs =
      this.state.speed === 'fast' ? 2000 : this.state.speed === 'slow' ? 5000 : 3500;

    this.timer = setInterval(() => {
      const curr = this.state.currentStep;
      if (curr >= 12) {
        this.pauseAutoPlay();
      } else {
        this.executeStep(curr + 1);
      }
    }, intervalMs);
  }

  pauseAutoPlay() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.setState({ isPlaying: false });
  }

  setSpeed(speed: 'normal' | 'fast' | 'slow') {
    this.setState({ speed });
    if (this.state.isPlaying) {
      this.startAutoPlay();
    }
  }

  // Natural appointment booking (called from Kiosk modal)
  async bookAppointment(
    data: Omit<AppointmentData, 'referenceCode' | 'createdAt'>
  ): Promise<AppointmentData> {
    const nowTime = new Date().toLocaleTimeString();
    const code = `APT-${Math.floor(1000 + Math.random() * 9000)}`;

    const aptData: AppointmentData = {
      ...data,
      referenceCode: code,
      createdAt: nowTime,
    };

    const aptRecord: AppointmentRecord = {
      id: `apt-${Date.now()}`,
      referenceCode: code,
      visitorName: data.visitorName,
      contact: data.contact,
      targetPerson: data.targetPerson,
      department: data.department,
      date: data.date,
      timeSlot: data.timeSlot,
      purpose: data.purpose,
      status: 'Confirmed',
      createdAt: nowTime,
    };

    this.setState((prev) => ({
      activeAppointment: aptData,
      appointments: [aptRecord, ...prev.appointments],
      activeAction: `Confirmed Appointment ${code} for ${data.department}`,
    }));

    this.logLiveEvent(
      'appointment_booked',
      `Confirmed Appointment ${code} for ${data.department} (${data.visitorName} - ${data.timeSlot})`
    );

    return aptData;
  }

  // Natural ticket creation (called from Kiosk modal)
  async createTicket(
    data: Omit<TicketData, 'ticketId' | 'status' | 'createdAt'>
  ): Promise<TicketData> {
    const nowTime = new Date().toLocaleTimeString();
    const id = `TCK-${Math.floor(2000 + Math.random() * 8000)}`;

    const ticketData: TicketData = {
      ...data,
      ticketId: id,
      status: 'Open',
      createdAt: nowTime,
    };

    const ticketRecord: TicketRecord = {
      id: `tck-${Date.now()}`,
      ticketId: id,
      issue: data.issueSummary,
      department: data.department,
      priority: data.priority,
      status: 'Open',
      visitorName: data.visitorName,
      contact: data.contact,
      assignedStaff: 'Mrs. Sita Maharjan',
      createdAt: nowTime,
    };

    this.setState((prev) => ({
      activeTicket: ticketData,
      tickets: [ticketRecord, ...prev.tickets],
      activeAction: `Generated Support Ticket ${id} for ${data.department}`,
    }));

    this.logLiveEvent(
      'ticket_created',
      `Generated Support Ticket ${id} for ${data.department} (${data.priority} Priority)`
    );

    return ticketData;
  }

  // Acknowledge handoff alert from Dashboard
  acknowledgeHandoff(notes?: string) {
    this.setState((prev) => ({
      handoffAlert: prev.handoffAlert ? { ...prev.handoffAlert, isActive: false } : null,
      currentVisitor: prev.currentVisitor
        ? { ...prev.currentVisitor, status: 'Completed' }
        : null,
      activeAction: `Staff accepted handoff at Counter A-102. ${notes || ''}`,
    }));

    this.logLiveEvent(
      'session_ended',
      `Staff at Counter A-102 accepted visitor handoff. ${notes || ''}`
    );
  }

  // Request handoff
  requestHandoff(reason?: string) {
    const nowTime = new Date().toLocaleTimeString();
    this.setState((prev) => ({
      receptionState: 'HANDOFF',
      currentVisitor: prev.currentVisitor
        ? { ...prev.currentVisitor, status: 'Needs staff' }
        : null,
      handoffAlert: {
        isActive: true,
        reason: reason || 'Visitor requested human front-desk staff assistance',
        visitorCode: prev.currentVisitor?.code || 'VIS-1045',
        counter: 'Counter A-102',
        dutyOfficer: 'Mr. Sunil Sharma',
        time: nowTime,
      },
    }));

    this.logLiveEvent(
      'handoff_requested',
      'Human handoff requested → Counter A-102 terminal notified'
    );
  }
}

export const demoStore = new DemoStoreClass();

// Custom React hook for reactive subscription
export function useDemoStore(): DemoState {
  const [state, setState] = useState<DemoState>(() => demoStore.getState());

  useEffect(() => {
    const unsubscribe = demoStore.subscribe(() => {
      setState(demoStore.getState());
    });
    return unsubscribe;
  }, []);

  return state;
}
