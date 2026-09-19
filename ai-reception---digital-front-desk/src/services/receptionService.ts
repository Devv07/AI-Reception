import { AIActionResponse, AppointmentData, TicketData } from '../types/reception';
import { apiClient, BackendAIResponse } from './apiClient';

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

  static async startConversation(): Promise<string> {
    const created = await apiClient.startConversation({ channel: 'web' });
    sessionStorage.setItem('ai-reception.conversation-id', created.conversation_id);
    return created.conversation_id;
  }

  static async queryAssistant(query: string, _lang: 'ne' | 'en', conversationId?: string): Promise<AIActionResponse & { isUnknown?: boolean; conversationId: string }> {
    const activeConversationId = conversationId || sessionStorage.getItem('ai-reception.conversation-id') || await ReceptionService.startConversation();
    const response = await apiClient.sendMessage(activeConversationId, query);
    return ReceptionService.toUiResponse(response.ai_response, activeConversationId);
  }

  private static toUiResponse(response: BackendAIResponse, conversationId: string): AIActionResponse & { isUnknown?: boolean; conversationId: string } {
    const action = response.action === 'get_department' ? 'department_redirect' : response.action === 'answer_question' || response.action === null ? 'answer' : response.action;
    return {
      answerEn: response.answer,
      answerNe: response.answer,
      intent: response.intent,
      action,
      sources: response.sources.map((source, index) => ({
        id: source.id || `backend-source-${index}`,
        title: source.title || source.source || 'Verified knowledge source',
        document: source.document || source.source || 'Backend knowledge source',
        page: Number(source.page || 0),
        section: source.section || '',
        excerpt: source.excerpt || '',
        confidence: Number(source.confidence || source.score || response.confidence),
        lastUpdated: source.lastUpdated || '',
      })),
      needsHuman: response.needs_human,
      isUnknown: response.intent === 'unknown',
      conversationId,
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
  static async bookAppointment(appointment: Omit<AppointmentData, 'referenceCode' | 'createdAt'>, conversationId?: string): Promise<AppointmentData> {
    const dateMatch = appointment.date.match(/([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})/);
    const date = dateMatch ? new Date(dateMatch[1]).toISOString().slice(0, 10) : appointment.date;
    const activeConversationId = conversationId || sessionStorage.getItem('ai-reception.conversation-id') || await ReceptionService.startConversation();
    const response = await apiClient.sendMessage(activeConversationId, `Book an appointment with ${appointment.department} on ${date} at ${appointment.timeSlot} for ${appointment.purpose}`);
    const referenceCode = response.message.id.slice(0, 8).toUpperCase();
    return { ...appointment, date, referenceCode: `APT-${referenceCode}`, createdAt: new Date().toLocaleTimeString() };
  }

  /**
   * Generate an official support ticket.
   */
  static async createTicket(ticket: Omit<TicketData, 'ticketId' | 'status' | 'createdAt'>, conversationId?: string): Promise<TicketData> {
    const activeConversationId = conversationId || sessionStorage.getItem('ai-reception.conversation-id') || await ReceptionService.startConversation();
    const response = await apiClient.sendMessage(activeConversationId, `Complaint for ${ticket.department}: ${ticket.issueSummary}`);
    const ticketId = response.ai_response.answer.match(/ticket ([0-9a-f-]+)/i)?.[1] || response.message.id.slice(0, 8).toUpperCase();
    return { ...ticket, ticketId: `TCK-${ticketId}`, status: 'Open', createdAt: new Date().toLocaleTimeString() };
  }
}
