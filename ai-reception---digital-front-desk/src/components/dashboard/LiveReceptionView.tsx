import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Activity,
  Radio,
  Clock,
  Sparkles,
  BookOpen,
  Bell,
  RefreshCw,
  CheckCircle2,
  ChevronRight,
  Zap,
} from 'lucide-react';
import { useDemoStore, demoStore } from '../../services/demoStore';
import { AIOrb } from '../reception/AIOrb';
import { LiveEventItem } from '../../types/dashboard';

interface LiveReceptionViewProps {
  onNavigateToConversation?: (id: string) => void;
  onNavigate?: (route: string) => void;
}

export const LiveReceptionView: React.FC<LiveReceptionViewProps> = ({
  onNavigateToConversation,
  onNavigate,
}) => {
  const demo = useDemoStore();
  const [isSimulatingEvent, setIsSimulatingEvent] = useState(false);

  const kioskStatus = 'Online';
  const kioskId = 'KIOSK-LOBBY-01';
  const cameraActive = demo.sensorActive;
  const lastPing = `Synchronized (${new Date().toLocaleTimeString()})`;

  const currentVisitor = demo.currentVisitor || {
    code: 'VIS-1044',
    name: 'Aayush Shrestha',
    status: 'In Conversation',
    arrival: '10:38 AM',
    waitingDuration: '1m 20s',
    currentLocation: 'Front Desk Kiosk A-01',
  };

  const currentAiState = demo.receptionState;
  const currentIntent =
    demo.intent ||
    (demo.receptionState === 'HANDOFF'
      ? 'Direct Front-Desk Duty Officer Handoff'
      : demo.receptionState === 'IDLE'
      ? 'Awaiting Visitor Arrival'
      : 'Undergraduate Program Inquiries');

  const confidence = demo.confidence || (demo.sources.length > 0 ? demo.sources[0].confidence : 0.985);
  const retrievedSource = demo.sources.length > 0 ? demo.sources[0] : null;
  const activeAction =
    demo.activeAction ||
    (demo.receptionState === 'IDLE'
      ? 'Awaiting visitor interaction at physical kiosk'
      : 'Processing interaction stream');

  const currentConversation =
    demo.conversations.find((c) => c.id === 'cnv-101') || demo.conversations[0];
  const liveEvents = demo.liveEvents;
  const handoffAlert = demo.handoffAlert;

  const showHandoffBanner = handoffAlert?.isActive;

  const handleAcknowledgeHandoff = () => {
    demoStore.acknowledgeHandoff('Officer Sunil Sharma dispatched to Counter A-102');
  };

  const handleSimulateVisitorPing = () => {
    setIsSimulatingEvent(true);
    demoStore.executeStep(1);
    setTimeout(() => setIsSimulatingEvent(false), 800);
  };

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Top Operations Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center">
            <span className="h-3.5 w-3.5 rounded-full bg-emerald-500 animate-ping absolute" />
            <span className="h-3.5 w-3.5 rounded-full bg-emerald-500" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white tracking-tight">
                Live AI Reception Operations Center
              </h2>
              <span className="px-2 py-0.5 rounded-md bg-blue-950 border border-blue-800 text-[11px] font-mono-code text-blue-400">
                {kioskId}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2 flex-wrap">
              <span>
                Status: <strong className="text-emerald-400">{kioskStatus}</strong>
              </span>
              <span>·</span>
              <span>
                Camera Sensor:{' '}
                <strong className={cameraActive ? 'text-cyan-400' : 'text-slate-400'}>
                  {cameraActive ? 'Active (Visitor Detected)' : 'Idle Scanning'}
                </strong>
              </span>
              <span>·</span>
              <span>Telemetry: {lastPing}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-end md:self-auto">
          <button
            onClick={handleSimulateVisitorPing}
            disabled={isSimulatingEvent}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-xs font-medium text-slate-300 hover:text-white transition"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Simulate Presence</span>
          </button>
          <button
            onClick={() => demoStore.executeStep(demo.currentStep === 0 ? 1 : demo.currentStep)}
            title="Refresh sync state"
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-400 hover:text-white transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Real-time Human Handoff Alert Banner */}
      <AnimatePresence>
        {showHandoffBanner && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 rounded-2xl bg-amber-950/70 border-2 border-amber-500/80 shadow-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                <Bell className="w-5 h-5 animate-bounce" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-300 font-mono-code">
                    Active Human Handoff Request
                  </span>
                  <span className="text-xs text-amber-400/80 font-mono-code">
                    [{handoffAlert.time || 'Just now'}]
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-white mt-0.5">
                  Visitor <span className="text-amber-200">{handoffAlert.visitorCode}</span> requested duty staff for counseling.
                </h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Target: <strong className="text-amber-300">{handoffAlert.counter}</strong> · Duty Officer:{' '}
                  <strong className="text-white">{handoffAlert.dutyOfficer}</strong>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto shrink-0">
              <button
                onClick={handleAcknowledgeHandoff}
                className="flex-1 sm:flex-initial px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition flex items-center justify-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Acknowledge & Dispatch Staff</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3-Column AI Operations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Column 1: Live Reception Monitor & Visitor Card (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          {/* Physical Kiosk Monitor Screen Viewport */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-4 shadow-xl overflow-hidden flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-rose-500 animate-pulse" />
                <span className="text-xs font-bold text-slate-200">Kiosk Screen Mirror</span>
              </div>
              <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                1080p · 60 FPS
              </span>
            </div>

            {/* Simulated Live Kiosk Display Viewport */}
            <div className="relative aspect-video rounded-xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center overflow-hidden p-3 group">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(30,58,138,0.25),transparent_70%)] pointer-events-none" />

              {/* Scaled AI Orb Visualizer matching current AI state */}
              <div className="scale-75 origin-center">
                <AIOrb state={currentAiState} />
              </div>

              {/* Overlaid Kiosk Telemetry */}
              <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-0.5 rounded bg-black/70 backdrop-blur-sm text-[10px] font-mono-code text-cyan-400 border border-cyan-500/20">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-ping" />
                <span>AI State: {currentAiState}</span>
              </div>

              <div className="absolute bottom-2 right-2 text-[10px] font-mono-code text-slate-400 bg-black/70 px-2 py-0.5 rounded backdrop-blur-sm">
                Lobby Block A (Front Desk)
              </div>
            </div>

            {/* Current Visitor Presence Card */}
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300">Active Visitor Profile</span>
                <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/50 text-amber-300">
                  {currentVisitor.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[11px] text-slate-500 block">Identifier</span>
                  <strong className="text-slate-200 font-mono-code">{currentVisitor.code}</strong>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500 block">Identified Name</span>
                  <strong className="text-slate-200">{currentVisitor.name}</strong>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500 block">Arrival Time</span>
                  <span className="text-slate-300 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-500" />
                    {currentVisitor.arrival}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500 block">At Front Desk</span>
                  <span className="text-slate-300">{currentVisitor.waitingDuration}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Column 2: Current Conversation & Intelligence Engine (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-4 shadow-xl flex flex-col gap-3 h-full">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-slate-200">Live AI Reasoning & RAG Retrieval</h3>
              </div>
              {currentConversation && (
                <button
                  onClick={() => onNavigateToConversation?.(currentConversation.id)}
                  className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 transition"
                >
                  <span>Full Log</span>
                  <ChevronRight className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* AI Intelligence Stats Pill Bar */}
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 font-mono-code uppercase block">Classified Intent</span>
                <span className="text-xs font-semibold text-cyan-300 line-clamp-1">{currentIntent}</span>
                <span className="text-[10px] text-emerald-400 mt-0.5 block font-mono-code">
                  {(confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 font-mono-code uppercase block">Active AI Action</span>
                <span className="text-xs font-semibold text-amber-300 line-clamp-1">{activeAction}</span>
                <span className="text-[10px] text-slate-400 mt-0.5 block font-mono-code">
                  Kiosk A-01 Sync
                </span>
              </div>
            </div>

            {/* Retrieved Knowledge Card */}
            <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-800/40 space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs text-blue-300 font-semibold">
                  <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                  <span>Grounding Document Evidence</span>
                </div>
                <span className="text-[10px] font-mono-code text-blue-400 bg-blue-900/50 px-1.5 py-0.5 rounded">
                  RAG Grounded
                </span>
              </div>
              <p className="text-xs text-slate-200 font-medium">
                {retrievedSource
                  ? `${retrievedSource.title} (Page ${retrievedSource.page || 1})`
                  : 'TCMIT Admissions Prospectus 2026.pdf (Section 3.2)'}
              </p>
              <p className="text-[11px] text-slate-400 italic bg-slate-950/50 p-2 rounded-lg border border-slate-800">
                {retrievedSource
                  ? `"${retrievedSource.excerpt}"`
                  : '"BIT requires minimum +2 aggregate GPA 2.0 or second division with Mathematics / Computer Science."'}
              </p>
            </div>

            {/* Transcript Messages Stream */}
            <div className="flex-1 space-y-2.5 overflow-y-auto max-h-72 p-1">
              {currentConversation?.messages.map((msg: any) => (
                <div
                  key={msg.id}
                  className={`flex flex-col gap-1 ${
                    msg.sender === 'USER'
                      ? 'items-end'
                      : msg.sender === 'STAFF'
                      ? 'items-center'
                      : 'items-start'
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono-code">
                    <span>{msg.sender}</span>
                    <span>·</span>
                    <span>{msg.timestamp}</span>
                  </div>

                  <div
                    className={`max-w-[88%] p-3 rounded-2xl text-xs leading-relaxed ${
                      msg.sender === 'USER'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : msg.sender === 'STAFF'
                        ? 'bg-amber-950/80 border border-amber-600/50 text-amber-200 text-center'
                        : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700/60'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Column 3: Real-Time Event Timeline (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-4 shadow-xl flex flex-col gap-3 h-full">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-slate-200">Real-Time Event Stream</h3>
              </div>
              <span className="text-[10px] font-mono-code text-slate-500">Live feed</span>
            </div>

            {/* Streaming Event Items */}
            <div className="space-y-2.5 overflow-y-auto max-h-[500px] pr-1">
              {liveEvents.map((ev: LiveEventItem) => {
                const isAlert = ev.type === 'handoff_requested';
                const isSuccess = ev.type === 'appointment_booked' || ev.type === 'ticket_created';
                return (
                  <div
                    key={ev.id}
                    className={`p-2.5 rounded-xl border text-xs transition ${
                      isAlert
                        ? 'bg-amber-950/40 border-amber-600/40 text-amber-200'
                        : isSuccess
                        ? 'bg-emerald-950/30 border-emerald-600/40 text-emerald-200'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono-code mb-1">
                      <span className={isAlert ? 'text-amber-400 font-bold' : 'text-cyan-400'}>
                        {ev.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-slate-500">{ev.time}</span>
                    </div>
                    <p className="text-[11px] leading-snug">{ev.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
