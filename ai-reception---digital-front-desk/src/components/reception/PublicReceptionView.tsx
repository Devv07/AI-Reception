import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  ReceptionState,
  LanguageMode,
  KnowledgeSource,
  AppointmentData,
  TicketData,
} from '../../types/reception';
import { TCMIT_INFO, KNOWLEDGE_SOURCES } from '../../data/tcmitData';
import { ReceptionService } from '../../services/receptionService';
import { demoStore, useDemoStore } from '../../services/demoStore';
import { ReceptionHeader } from './ReceptionHeader';
import { VRMAvatar } from './VRMAvatar';
import { SpeechTranscript } from './SpeechTranscript';
import { VoiceControls } from './VoiceControls';
import { TextInputFallback } from './TextInputFallback';
import { AppointmentBookingModal } from './AppointmentBookingModal';
import { TicketCreationModal } from './TicketCreationModal';
import { HumanHandoffCard } from './HumanHandoffCard';
import { UnknownQuestionCard } from './UnknownQuestionCard';
import { DepartmentDirectoryModal } from './DepartmentDirectoryModal';
import { CompletionCard } from './CompletionCard';
import { DemoController } from './DemoController';
import {
  Sparkles,
  Keyboard,
  GraduationCap,
  Calendar,
  ReceiptText,
  Building2,
  UserCheck,
} from 'lucide-react';

interface PublicReceptionViewProps {
  onNavigateToDashboard?: () => void;
  currentPath?: string;
  onNavigate?: (path: string) => void;
  isSplitView?: boolean;
  onToggleSplitView?: () => void;
}

export const PublicReceptionView: React.FC<PublicReceptionViewProps> = ({
  onNavigateToDashboard,
  currentPath,
  onNavigate,
  isSplitView,
  onToggleSplitView,
}) => {
  const [conversationId, setConversationId] = React.useState<string | null>(() => sessionStorage.getItem('ai-reception.conversation-id'));
  // Shared reactive demo state
  const demo = useDemoStore();
  const state = demo.receptionState;
  const language: LanguageMode = demo.language;
  const audioEnabled = demo.audioEnabled;
  const sensorActive = demo.sensorActive;
  const userQuery = demo.userQuery;
  const aiResponse = demo.aiResponse;
  const sources = demo.sources;
  const intent = demo.intent;
  const activeAppointment = demo.activeAppointment;
  const activeTicket = demo.activeTicket;
  const isDirectoryOpen = demo.isDirectoryOpen;
  const isTextDrawerOpen = demo.isTextDrawerOpen;

  useEffect(() => {
    if (demo.language !== 'en') demoStore.setState({ language: 'en' });
  }, [demo.language]);

  // Speech cancel ref
  const cancelSpeechRef = useRef<(() => void) | null>(null);
  const recognitionRef = useRef<any>(null);

  // Cleanup speech synthesis on unmount
  useEffect(() => {
    return () => {
      if (cancelSpeechRef.current) cancelSpeechRef.current();
    };
  }, []);

  // Handle Speech Output
  const speakResponse = (text: string, lang: 'ne' | 'en') => {
    if (!audioEnabled) return;
    if (cancelSpeechRef.current) cancelSpeechRef.current();

    demoStore.setState({ receptionState: 'SPEAKING' });
    cancelSpeechRef.current = ReceptionService.speak(
      text,
      lang,
      () => demoStore.setState({ receptionState: 'SPEAKING' }),
      () => {
        // Once done speaking, prompt completion or action
        if (demoStore.getState().receptionState === 'SPEAKING') {
          demoStore.setState({ receptionState: 'COMPLETED' });
        }
      }
    );
  };

  const handleStopSpeaking = () => {
    if (cancelSpeechRef.current) {
      cancelSpeechRef.current();
    }
    demoStore.setState({ receptionState: 'COMPLETED' });
  };

  // Replay speech
  const handleReplayAudio = () => {
    if (!aiResponse) return;
    const textToSpeak = language === 'ne' ? aiResponse.ne : aiResponse.en;
    speakResponse(textToSpeak, language === 'ne' ? 'ne' : 'en');
  };

  // Trigger Query Processing
  const processVisitorInquiry = async (queryText: string) => {
    demoStore.setState({
      userQuery: queryText,
      receptionState: 'THINKING',
      activeAction: 'Analyzing query via Gemini NLU & RAG Vector Store...',
    });
    demoStore.logLiveEvent('transcript', `Visitor voice input: "${queryText}"`);

    try {
      const result = await ReceptionService.queryAssistant(
        queryText,
        'en',
        conversationId || undefined
      );
      setConversationId(result.conversationId);

      // Handle Unknown Question / Non-verified state
      if (result.isUnknown) {
        demoStore.setState({
          aiResponse: { en: result.answerEn, ne: result.answerNe },
          sources: [],
          intent: result.intent,
          receptionState: 'UNKNOWN_QUESTION',
          activeAction: 'Unverified boundary hit. Escalating to human desk.',
        });
        demoStore.logLiveEvent('intent_classified', `Unknown query intent: "${result.intent}"`);
        return;
      }

      demoStore.setState({
        aiResponse: { en: result.answerEn, ne: result.answerNe },
        sources: result.sources || [],
        intent: result.intent,
        activeAction: `Intent identified: ${result.intent}. Delivering verified response.`,
      });
      demoStore.logLiveEvent('intent_classified', `Intent: ${result.intent}`);

      if (result.sources && result.sources.length > 0) {
        demoStore.logLiveEvent(
          'source_retrieved',
          `RAG retrieved: "${result.sources[0].title}" (${result.sources[0].confidence * 100}% match)`
        );
      }

      if (result.action === 'book_appointment') {
        demoStore.setState({ receptionState: 'ACTION_APPOINTMENT' });
      } else if (result.action === 'create_ticket') {
        demoStore.setState({ receptionState: 'ACTION_TICKET' });
      } else if (result.action === 'human_handoff') {
        demoStore.requestHandoff(result.answerEn);
      } else if (result.action === 'department_redirect') {
        demoStore.setState({ isDirectoryOpen: true });
          speakResponse(result.answerEn, 'en');
      } else {
        speakResponse(result.answerEn, 'en');
      }
    } catch {
      demoStore.setState({ receptionState: 'IDLE' });
    }
  };

  // Real Microphone Recognition with Fallback
  const handleStartListening = () => {
    ReceptionService.playChime('wake');
    demoStore.setState({
      receptionState: 'LISTENING',
      userQuery: language === 'ne' ? 'आवाज सुन्दैछ...' : 'Listening to voice...',
      activeAction: 'Microphone streaming audio to speech engine...',
    });
    demoStore.logLiveEvent('transcript', 'Voice listener activated at Kiosk A-01');

    // Attempt Web Speech API if supported
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.lang = language === 'ne' ? 'ne-NP' : 'en-US';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          demoStore.setState({ userQuery: transcript });
          if (event.results[0].isFinal) {
            recognition.stop();
            processVisitorInquiry(transcript);
          }
        };

        recognition.onerror = () => {
          // If error/blocked in iframe, default to realistic sample query
          setTimeout(() => {
            const fallbackQuery =
              language === 'ne'
                ? 'मलाई BIT admission को लागि के के चाहिन्छ?'
                : 'What are the BIT admission requirements?';
            processVisitorInquiry(fallbackQuery);
          }, 1500);
        };

        recognitionRef.current = recognition;
        recognition.start();
        return;
      } catch {
        // Fallback simulation
      }
    }

    // Fallback simulation for environments without Web Speech permission
    setTimeout(() => {
      const sample =
        language === 'ne'
          ? 'मलाई BIT admission को लागि के के चाहिन्छ?'
          : 'What are the BIT admission requirements?';
      processVisitorInquiry(sample);
    }, 2200);
  };

  const handleStopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    if (state === 'LISTENING') {
      const sample =
        language === 'ne'
          ? 'मलाई BIT admission को लागि के के चाहिन्छ?'
          : 'What are the BIT admission requirements?';
      processVisitorInquiry(sample);
    }
  };

  // Quick prompt selection
  const handleSelectQuickPrompt = (prompt: string) => {
    processVisitorInquiry(prompt);
  };

  // State 2: Visitor Detected Transition
  const triggerVisitorDetection = () => {
    ReceptionService.playChime('wake');
    demoStore.executeStep(1);
    setTimeout(() => {
      if (demoStore.getState().receptionState === 'VISITOR_DETECTED') {
        demoStore.setState({ receptionState: 'GREETING' });
      }
    }, 700);
    setTimeout(() => {
      if (demoStore.getState().receptionState === 'GREETING') {
        demoStore.setState({ receptionState: 'IDLE' });
      }
    }, 3200);
  };

  // Reset to ambient idle
  const handleResetToIdle = () => {
    if (cancelSpeechRef.current) cancelSpeechRef.current();
    demoStore.resetToIdle();
  };

  return (
    <div className="relative w-full h-full min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between overflow-hidden select-none">
      {/* Background Architectural Glow & Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(30,58,138,0.25),rgba(255,255,255,0))] pointer-events-none" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b08_1px,transparent_1px),linear-gradient(to_bottom,#1e293b08_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />

      {/* 1. Reception Kiosk Header */}
      <ReceptionHeader
        language={language}
        onLanguageChange={() => demoStore.setState({ language: 'en' })}
        audioEnabled={audioEnabled}
        onToggleAudio={() => demoStore.setState({ audioEnabled: !audioEnabled })}
        sensorActive={sensorActive}
        onTriggerPresence={triggerVisitorDetection}
        onNavigateToDashboard={onNavigateToDashboard || (() => onNavigate?.('/dashboard/live'))}
      />

      {/* 2. Main Center Dynamic Reception Experience */}
      <main className="flex-1 flex flex-col items-center justify-center relative px-4 py-2 w-full max-w-5xl mx-auto overflow-y-auto">
        {/* State 1: Ambient Idle State */}
        {state === 'IDLE' && !userQuery && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center text-center gap-2 max-w-2xl z-10"
          >
            <VRMAvatar state="IDLE" onClick={triggerVisitorDetection} />

            <div className="space-y-1 mt-1">
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {language === 'ne' ? 'नमस्ते, स्वागत छ' : 'Namaste. Welcome.'}
              </h2>
              <p className="text-base sm:text-lg text-slate-300 font-normal">
                {language === 'ne'
                  ? 'म TCMIT को AI रिसेप्सनिस्ट हुँ। म तपाईंलाई कसरी सहयोग गर्न सक्छु?'
                  : "I'm your AI receptionist. How can I help you today?"}
              </p>
            </div>

            <div className="flex items-center gap-2 text-xs text-blue-400/90 font-medium my-1">
              <span className="flex h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
              <span>Physical Front Desk Online · Tap any service or speak naturally</span>
            </div>

            {/* Quick Touch Tiles for Reception Kiosk */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mt-3 w-full max-w-xl text-left">
              <button
                onClick={() =>
                  processVisitorInquiry(
                    language === 'ne'
                      ? 'मलाई BIT admission को लागि के के चाहिन्छ?'
                      : 'What are the BIT admission requirements?'
                  )
                }
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <GraduationCap className="w-4 h-4 text-blue-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">RAG Info</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {language === 'ne' ? 'BIT भर्ना जानकारी' : 'BIT Admissions'}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  {language === 'ne' ? 'योग्यता र कागजातहरू' : 'Eligibility & prospectus'}
                </span>
              </button>

              <button
                onClick={() => {
                  demoStore.setState({
                    userQuery:
                      language === 'ne'
                        ? 'Principal लाई भेट्न appointment लिन मिल्छ?'
                        : 'Can I schedule a meeting with the Principal?',
                    receptionState: 'ACTION_APPOINTMENT',
                  });
                }}
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <Calendar className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">Schedule</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {language === 'ne' ? 'भेटघाट समय (Appointment)' : 'Book Appointment'}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  {language === 'ne' ? 'कलेज प्रशासनसँग' : 'Principal or Admissions'}
                </span>
              </button>

              <button
                onClick={() => {
                  demoStore.setState({
                    userQuery:
                      language === 'ne'
                        ? 'मेरो admission payment मा समस्या भयो'
                        : 'I have an issue with admission fee payment',
                    receptionState: 'ACTION_TICKET',
                  });
                }}
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <ReceiptText className="w-4 h-4 text-amber-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">Support</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {language === 'ne' ? 'समस्या दर्ता (Ticket)' : 'Create Ticket'}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  {language === 'ne' ? 'शुल्क वा प्राविधिक समस्या' : 'Fee or technical issue'}
                </span>
              </button>

              <button
                onClick={() => demoStore.setState({ isDirectoryOpen: true })}
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <Building2 className="w-4 h-4 text-purple-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">Campus</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {language === 'ne' ? 'विभाग र कोठा' : 'Department Guide'}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  {language === 'ne' ? 'स्थान र सम्पर्क' : 'Find office & floors'}
                </span>
              </button>

              <button
                onClick={() => {
                  demoStore.setState({
                    userQuery:
                      language === 'ne'
                        ? 'कर्मचारीसँग सिधा कुरा गर्न चाहन्छु'
                        : 'I want to speak with staff directly',
                    receptionState: 'HANDOFF',
                  });
                  demoStore.requestHandoff(
                    language === 'ne'
                      ? 'आगन्तुकले काउन्टर कर्मचारीसँग प्रत्यक्ष कुरा गर्न अनुरोध गर्नुभयो'
                      : 'Visitor explicitly requested front-desk duty officer'
                  );
                }}
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <UserCheck className="w-4 h-4 text-rose-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">Human Desk</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {language === 'ne' ? 'कर्मचारी बोलाउनुहोस्' : 'Human Handoff'}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  {language === 'ne' ? 'काउन्टर A-102 मा सूचना' : 'Front desk duty officer'}
                </span>
              </button>

              <button
                onClick={() => demoStore.setState({ language: 'en' })}
                className="p-3 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 transition group flex flex-col gap-1.5 shadow-md"
              >
                <div className="flex items-center justify-between">
                  <Sparkles className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition" />
                  <span className="text-[10px] text-slate-500 font-mono-code">Language</span>
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  English Reception
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1">
                  English voice and text support
                </span>
              </button>
            </div>
          </motion.div>
        )}

        {/* State 2: Visitor Detected State */}
        {state === 'VISITOR_DETECTED' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            className="flex flex-col items-center text-center gap-3"
          >
            <VRMAvatar state="VISITOR_DETECTED" />
            <div className="p-3 bg-blue-950/60 border border-blue-500/50 rounded-2xl backdrop-blur-sm max-w-md">
              <div className="flex items-center justify-center gap-2 text-xs font-semibold text-blue-300 mb-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>CAMERA PROXIMITY SENSOR TRIGGERED</span>
              </div>
              <h3 className="text-xl font-bold text-white">
                {language === 'ne' ? 'आगन्तुक पहिचान भयो' : 'Visitor Detected'}
              </h3>
              <p className="text-sm text-slate-300 mt-1">
                {language === 'ne'
                  ? 'नमस्ते! TCMIT मा स्वागत छ। कृपया माइक्रोफोनमा बोल्नुहोस्।'
                  : 'Hello! Welcome to TCMIT. Please speak or tap to interact.'}
              </p>
            </div>
          </motion.div>
        )}

        {/* States 3, 4, 5: Listening, Thinking, Speaking Conversation View */}
        {(state === 'GREETING' ||
          state === 'LISTENING' ||
          state === 'THINKING' ||
          state === 'SPEAKING' ||
          (userQuery && state === 'IDLE')) && (
          <div className="w-full flex flex-col items-center gap-3 max-w-3xl">
            <VRMAvatar
              state={state}
              onClick={state === 'SPEAKING' ? handleStopSpeaking : undefined}
            />

            <SpeechTranscript
              isSpeaking={state === 'SPEAKING'}
              language={language}
              userQuery={userQuery}
              aiResponse={aiResponse}
              sources={sources}
              intent={intent}
              onReplayAudio={handleReplayAudio}
            />
          </div>
        )}

        {/* State 6: Appointment Booking Action */}
        {state === 'ACTION_APPOINTMENT' && (
          <AppointmentBookingModal
            onCancel={() => demoStore.setState({ receptionState: 'IDLE' })}
            onConfirm={async (data) => {
              ReceptionService.playChime('success');
              await ReceptionService.bookAppointment(data, conversationId || undefined);
              await demoStore.bookAppointment(data);
              demoStore.setState({ receptionState: 'COMPLETED' });
            }}
            language={language}
          />
        )}

        {/* State 7: Support Ticket Creation Action */}
        {state === 'ACTION_TICKET' && (
          <TicketCreationModal
            onCancel={() => demoStore.setState({ receptionState: 'IDLE' })}
            onConfirm={async (data) => {
              ReceptionService.playChime('success');
              await ReceptionService.createTicket(data, conversationId || undefined);
              await demoStore.createTicket(data);
              demoStore.setState({ receptionState: 'COMPLETED' });
            }}
            language={language}
          />
        )}

        {/* State 8: Human Duty Officer Handoff */}
        {state === 'HANDOFF' && (
          <div className="w-full max-w-lg">
            <HumanHandoffCard
              onDone={handleResetToIdle}
              language={language}
            />
          </div>
        )}

        {/* State 9: Unknown Question / Responsible AI Boundary */}
        {state === 'UNKNOWN_QUESTION' && (
          <div className="w-full max-w-lg">
            <UnknownQuestionCard
              onConnectStaff={() => {
                demoStore.requestHandoff('Visitor inquiry outside verified knowledge base');
              }}
              onAskSomethingElse={handleResetToIdle}
              language={language}
            />
          </div>
        )}

        {/* State 10: Task Completed Screen */}
        {state === 'COMPLETED' && (
          <div className="w-full max-w-lg">
            <CompletionCard
              onAskAnother={handleResetToIdle}
              onFinished={handleResetToIdle}
              language={language}
            />
          </div>
        )}
      </main>

      {/* 3. Bottom Kiosk Control Bar (Voice + Fallback Input) */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md py-3.5 z-20">
        <VoiceControls
          state={state}
          language={language}
          onStartListening={handleStartListening}
          onStopListening={handleStopListening}
          onStopSpeaking={handleStopSpeaking}
          onOpenTextInput={() => demoStore.setState({ isTextDrawerOpen: true })}
          onSelectQuickPrompt={handleSelectQuickPrompt}
        />
      </footer>

      {/* Text Input Fallback Modal Drawer */}
      <TextInputFallback
        isOpen={isTextDrawerOpen}
        onClose={() => demoStore.setState({ isTextDrawerOpen: false })}
        onSubmit={processVisitorInquiry}
        language={language}
      />

      {/* Campus Directory Modal */}
      <DepartmentDirectoryModal
        isOpen={isDirectoryOpen}
        onClose={() => demoStore.setState({ isDirectoryOpen: false })}
        language={language}
      />

      {/* 4. Hackathon Presentation Event Simulator Controller */}
      <DemoController
        currentPath={currentPath || '/reception'}
        onNavigate={onNavigate || onNavigateToDashboard}
        isSplitView={isSplitView}
        onToggleSplitView={onToggleSplitView}
      />
    </div>
  );
};
