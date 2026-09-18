import { AIActionResponse, AppointmentData, TicketData } from '../types/reception';
import { KNOWLEDGE_SOURCES } from '../data/tcmitData';

export class ReceptionService {
  /**
   * Generates a subtle synthesized dual-tone audio chime using Web Audio API.
   */
  static playChime(type: 'wake' | 'success' | 'alert' = 'wake') {
    if (typeof window === 'undefined') return;
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContextClass) return;
      const ctx = new AudioContextClass();
      const now = ctx.currentTime;

      if (type === 'wake') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.12); // E5
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'success') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880.0, now + 0.15); // A5
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.4);
      } else {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(440.0, now);
        osc.frequency.exponentialRampToValueAtTime(349.23, now + 0.2);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.3);
      }
    } catch {}
  }

  /**
   * Simulates AI reception natural language understanding & RAG retrieval.
   * Matches structured AI output model specified for FastAPI backend integration.
   */
  static async queryAssistant(query: string, lang: 'ne' | 'en'): Promise<AIActionResponse & { isUnknown?: boolean }> {
    // Artificial latency for authentic thinking state demonstration (1.2s - 1.5s)
    await new Promise((resolve) => setTimeout(resolve, 1300));

    const normalized = query.toLowerCase();

    // 1. Unknown / Non-verified question (Prompt requirement 12)
    if (
      normalized.includes('unknown') ||
      normalized.includes('confidential') ||
      normalized.includes('secret') ||
      normalized.includes('salary') ||
      normalized.includes('test unknown') ||
      normalized.includes('थाहा छैन')
    ) {
      return {
        answerEn: "I don't have enough verified information to answer that confidently. I can connect you with a staff member.",
        answerNe: 'मलाई यो प्रश्नको जवाफ दिन पर्याप्त प्रमाणित जानकारी छैन। म तपाईंलाई हाम्रा कर्मचारीसँग जोड्न सक्छु।',
        intent: 'Unverified Knowledge Domain',
        action: 'human_handoff',
        sources: [],
        needsHuman: true,
        isUnknown: true,
      };
    }

    // 2. Department Directory / Campus Locations (Prompt requirement 16)
    if (
      normalized.includes('where is') ||
      normalized.includes('department') ||
      normalized.includes('directory') ||
      normalized.includes('कहाँ छ') ||
      normalized.includes('शाखा') ||
      normalized.includes('location') ||
      normalized.includes('room')
    ) {
      return {
        answerEn:
          'TCMIT Campus has 3 main blocks: Admissions is at Block A Ground Floor (Room A-102), Accounts is at Block A 1st Floor (Room A-204), and the Principal\'s Office is in Block B 2nd Floor (Room B-201). Opening the campus directory for you.',
        answerNe:
          'TCMIT क्याम्पसमा ३ वटा मुख्य ब्लक छन्: भर्ना शाखा ब्लक A भुइँतल्ला (कोठा A-102), लेखा शाखा ब्लक A पहिलो तल्ला (कोठा A-204), र प्रिन्सिपल कार्यालय ब्लक B दोस्रो तल्ला (कोठा B-201) मा छ। म क्याम्पस निर्देशिका खोल्दैछु।',
        intent: 'Campus Directory & Navigation',
        action: 'department_redirect',
        sources: [
          {
            id: 'src-campus-dir',
            title: 'TCMIT Campus Guide & Floor Map',
            document: 'Campus Directory & Facilities.pdf',
            page: 1,
            section: 'Section 1: Academic Blocks & Counter Numbers',
            excerpt:
              'Main Reception is situated at Ground Floor Block A. Visitor access to Administrative Blocks B and C is guided through Reception corridors with directional signage.',
            confidence: 0.99,
            lastUpdated: 'Verified Sep 2026',
          },
        ],
        needsHuman: false,
      };
    }

    // 3. BIT Admission Inquiry (Prompt requirement 10 & 48)
    if (
      normalized.includes('bit') ||
      normalized.includes('admission') ||
      normalized.includes('भर्ना') ||
      normalized.includes('requirements') ||
      normalized.includes('eligibility') ||
      normalized.includes('apply')
    ) {
      return {
        answerEn:
          'For BIT admission at TCMIT, you need a minimum Grade C in all subjects of 10+2 / PCL with Mathematics or Computer Science. You also require your TU/CMAT entrance scorecard, character certificate, and academic mark sheets. Applications for the Fall 2026 intake are currently open at Counter A-102.',
        answerNe:
          'TCMIT मा BIT भर्नाका लागि कक्षा १२ वा प्रवीणता प्रमाणपत्र तहमा कम्तीमा Grade C ल्याएको हुनुपर्छ (गणित वा कम्प्युटर साइन्स अनिवार्य)। साथै TU प्रवेश परीक्षाको Scorecard, ट्रान्सक्रिप्ट र चारित्रिक प्रमाणपत्र आवश्यक पर्दछ। भर्ना फारम काउन्टर A-102 मा उपलब्ध छ।',
        intent: 'Admissions Inquiry (BIT)',
        action: 'answer',
        sources: [KNOWLEDGE_SOURCES.bit_admission],
        needsHuman: false,
      };
    }

    // 4. Appointment Booking Request (e.g. Principal's meeting)
    if (
      normalized.includes('principal') ||
      normalized.includes('appointment') ||
      normalized.includes('भेट्न') ||
      normalized.includes('meeting') ||
      normalized.includes('समय') ||
      normalized.includes('schedule')
    ) {
      return {
        answerEn:
          "Certainly. I can schedule a direct appointment with the Principal's Executive Office (Prof. Dr. Rajendra Karki) in Block B-201. Available visitor consultation slots are between 10:00 AM and 1:30 PM. Please select your preferred date and time on the screen.",
        answerNe:
          'अवश्य। म प्रिन्सिपल कार्यालय (प्रा. डा. राजेन्द्र कार्की, कोठा B-201) सँग तपाईंको भेटघाटको समय तय गरिदिन्छु। अभिभावक र आगन्तुकका लागि बिहान १०:०० देखि दिउँसो १:३० सम्मको समय उपलब्ध छ। कृपया स्क्रिनमा आफ्नो उपयुक्त समय रोज्नुहोस्।',
        intent: "Executive Consultation (Principal's Office)",
        action: 'book_appointment',
        sources: [KNOWLEDGE_SOURCES.principal_policy],
        needsHuman: false,
      };
    }

    // 5. Payment Issue / Fee Problem
    if (
      normalized.includes('payment') ||
      normalized.includes('fee') ||
      normalized.includes('पैसा') ||
      normalized.includes('समस्या') ||
      normalized.includes('रकम') ||
      normalized.includes('fail') ||
      normalized.includes('receipt')
    ) {
      return {
        answerEn:
          "I understand your admission payment encountered a verification issue. I will generate an official priority support ticket for our Accounts and Admissions team immediately so it can be verified at the counter.",
        answerNe:
          'तपाईंको भर्ना शुल्क भुक्तानीमा समस्या देखिएकोमा क्षमाप्रार्थी छौं। म तुरुन्तै लेखा तथा भर्ना शाखाका लागि आधिकारिक Support Ticket दर्ता गरिदिन्छु, जसबाट काउन्टरमा सिधै समाधान हुनेछ।',
        intent: 'Payment Resolution / Support Ticket',
        action: 'create_ticket',
        sources: [KNOWLEDGE_SOURCES.payment_policy],
        needsHuman: false,
      };
    }

    // 6. Human Handoff / Talk to Staff
    if (
      normalized.includes('human') ||
      normalized.includes('staff') ||
      normalized.includes('कर्मचारी') ||
      normalized.includes('person') ||
      normalized.includes('help desk') ||
      normalized.includes('officer')
    ) {
      return {
        answerEn:
          'Connecting you directly to our front desk human officer at Counter A-102. A staff notification has been dispatched to their terminal.',
        answerNe:
          'म तपाईंलाई तुरुन्तै हाम्रो काउन्टर A-102 का ड्युटी अधिकृतसँग जोड्दैछु। तपाईंको उपस्थितिको सूचना कर्मचारी टर्मिनलमा पठाइएको छ।',
        intent: 'Direct Human Assistance',
        action: 'human_handoff',
        sources: [],
        needsHuman: true,
      };
    }

    // 7. Default / General inquiry
    return {
      answerEn:
        'TCMIT reception is ready to assist you. You can ask about undergraduate BIT admissions, schedule an appointment with the Principal, file an inquiry ticket, or locate any campus department.',
      answerNe:
        'TCMIT रिसेप्सनमा तपाईंलाई स्वागत छ। तपाईंले BIT भर्नाका नियमहरू, प्रिन्सिपलसँगको भेटघाट, शुल्क तथा समस्या समाधान, वा क्याम्पसका शाखाहरूबारे जानकारी लिन सक्नुहुन्छ।',
      intent: 'General Campus Assistance',
      action: 'answer',
      sources: [KNOWLEDGE_SOURCES.bit_admission],
      needsHuman: false,
    };
  }

  /**
   * Browser Text-to-Speech synthesis with fallback and natural speech simulation.
   */
  static speak(text: string, lang: 'ne' | 'en', onStart?: () => void, onEnd?: () => void): () => void {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      onStart?.();
      const timer = setTimeout(() => {
        onEnd?.();
      }, Math.min(Math.max(text.length * 60, 2500), 7000));
      return () => clearTimeout(timer);
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'ne' ? 'hi-IN' : 'en-US';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => onStart?.();
    utterance.onend = () => onEnd?.();
    utterance.onerror = () => onEnd?.();

    window.speechSynthesis.speak(utterance);

    return () => {
      window.speechSynthesis.cancel();
    };
  }

  /**
   * Generate an official appointment receipt.
   */
  static async bookAppointment(appointment: Omit<AppointmentData, 'referenceCode' | 'createdAt'>): Promise<AppointmentData> {
    await new Promise((r) => setTimeout(r, 600));
    const randomCode = Math.floor(1000 + Math.random() * 9000);
    return {
      ...appointment,
      referenceCode: `APT-${randomCode}`,
      createdAt: new Date().toLocaleTimeString(),
    };
  }

  /**
   * Generate an official support ticket.
   */
  static async createTicket(ticket: Omit<TicketData, 'ticketId' | 'status' | 'createdAt'>): Promise<TicketData> {
    await new Promise((r) => setTimeout(r, 600));
    const randomNum = Math.floor(2000 + Math.random() * 8000);
    return {
      ...ticket,
      ticketId: `TCK-${randomNum}`,
      status: 'Open',
      createdAt: new Date().toLocaleTimeString(),
    };
  }
}
