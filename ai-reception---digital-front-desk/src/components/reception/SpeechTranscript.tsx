import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { BookOpen, CheckCircle2, ChevronDown, ChevronUp, RotateCcw, Sparkles } from 'lucide-react';
import { KnowledgeSource, LanguageMode } from '../../types/reception';

interface SpeechTranscriptProps {
  userQuery: string | null;
  aiResponse: { en: string; ne: string } | null;
  sources?: KnowledgeSource[];
  intent?: string;
  isSpeaking: boolean;
  language: LanguageMode;
  onReplayAudio?: () => void;
  onSelectAction?: (actionId: string) => void;
}

export const SpeechTranscript: React.FC<SpeechTranscriptProps> = ({
  userQuery,
  aiResponse,
  sources,
  intent,
  isSpeaking,
  language,
  onReplayAudio,
  onSelectAction,
}) => {
  const [sourcesOpen, setSourcesOpen] = useState<boolean>(true);

  if (!userQuery && !aiResponse) {
    return null;
  }

  const activeAiText = language === 'ne' && aiResponse?.ne ? aiResponse.ne : aiResponse?.en;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 flex flex-col gap-3.5 z-20">
      {/* 1. Visitor Transcript Card */}
      {userQuery && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="self-end max-w-[90%] sm:max-w-[80%] rounded-2xl bg-slate-900/90 border border-slate-800 p-4 text-slate-100 shadow-md backdrop-blur-md"
        >
          <div className="flex items-center justify-between gap-3 mb-1.5 text-[11px] text-slate-400 font-medium">
            <span className="flex items-center gap-1.5 text-blue-400">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              Visitor Voice Transcript
            </span>
            <span className="font-mono-code">Live Input</span>
          </div>
          <p className="text-sm sm:text-base font-medium leading-relaxed tracking-wide text-slate-100">
            "{userQuery}"
          </p>
        </motion.div>
      )}

      {/* 2. AI Authoritative Response Card */}
      {aiResponse && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.05 }}
          className="self-start w-full rounded-2xl bg-gradient-to-b from-slate-900/95 to-slate-950/95 border border-slate-700/80 p-5 shadow-2xl shadow-black/60 backdrop-blur-md relative overflow-hidden"
        >
          {/* Subtle upper accent bar */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500" />

          {/* AI Header with Intent Tag */}
          <div className="flex items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              </div>
              <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                TCMIT Official Response
              </span>
              {isSpeaking && (
                <span className="flex items-center gap-1 text-[11px] text-cyan-400 bg-cyan-950/50 border border-cyan-500/30 px-2 py-0.5 rounded-full animate-pulse">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                  Speaking
                </span>
              )}
            </div>

            {intent && (
              <span className="text-[11px] px-2.5 py-0.5 rounded-md bg-slate-800/80 border border-slate-700 text-slate-300 font-mono-code">
                Intent: {intent}
              </span>
            )}
          </div>

          {/* Main AI Text */}
          <p
            className={`text-base sm:text-lg leading-relaxed text-slate-100 font-normal ${
              language === 'ne' ? 'font-nepali text-lg' : ''
            }`}
          >
            {activeAiText}
          </p>

          {/* Actions & Verification Bar */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
            {/* Replay voice button */}
            <button
              onClick={onReplayAudio}
              className="flex items-center gap-1.5 text-slate-400 hover:text-cyan-300 transition py-1 px-2.5 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-800"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Repeat Response</span>
            </button>

            {/* Grounded Source Toggle */}
            {sources && sources.length > 0 && (
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 transition py-1 px-2.5 rounded-lg bg-blue-950/40 border border-blue-800/60 font-medium"
              >
                <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                <span>Verified Source Evidence ({sources.length})</span>
                {sourcesOpen ? (
                  <ChevronUp className="w-3.5 h-3.5" />
                ) : (
                  <ChevronDown className="w-3.5 h-3.5" />
                )}
              </button>
            )}
          </div>

          {/* Expandable Knowledge Source Drawer */}
          <AnimatePresence>
            {sourcesOpen && sources && sources.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 overflow-hidden"
              >
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-cyan-900/40 text-xs">
                  {sources.map((src) => (
                    <div key={src.id} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between text-cyan-300 font-semibold">
                        <span className="flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          {src.document} · Page {src.page}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono-code">
                          {Math.round(src.confidence * 100)}% Match
                        </span>
                      </div>
                      <p className="text-slate-300 font-normal leading-relaxed italic bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/70">
                        "{src.excerpt}"
                      </p>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono-code pt-0.5">
                        <span>{src.section}</span>
                        <span>{src.lastUpdated}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
};
