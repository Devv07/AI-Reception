import React from 'react';
import { motion } from 'motion/react';
import { Mic, MicOff, Keyboard, Square, Sparkles } from 'lucide-react';
import { ReceptionState, LanguageMode } from '../../types/reception';

interface VoiceControlsProps {
  state: ReceptionState;
  language: LanguageMode;
  onStartListening: () => void;
  onStopListening: () => void;
  onStopSpeaking: () => void;
  onOpenTextInput: () => void;
  onSelectQuickPrompt: (prompt: string) => void;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  state,
  language,
  onStartListening,
  onStopListening,
  onStopSpeaking,
  onOpenTextInput,
  onSelectQuickPrompt,
}) => {
  const isListening = state === 'LISTENING';
  const isSpeaking = state === 'SPEAKING';
  const isBusy = state === 'THINKING';

  const quickPrompts =
    language === 'ne'
      ? [
          'मलाई BIT admission को लागि के के चाहिन्छ?',
          'Principal लाई भेट्न appointment लिन मिल्छ?',
          'मेरो admission payment मा समस्या भयो',
          'कर्मचारीसँग कुरा गर्न चाहन्छु',
        ]
      : [
          'What are the BIT admission requirements?',
          "Can I book an appointment with the Principal?",
          'I have an issue with my fee payment',
          'Can I speak with a staff member?',
        ];

  return (
    <div className="w-full max-w-xl mx-auto px-4 flex flex-col items-center gap-4 z-20 select-none">
      {/* Quick Intent Suggested Prompts Chips */}
      <div className="w-full flex flex-wrap items-center justify-center gap-2">
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuickPrompt(prompt)}
            disabled={isListening || isBusy}
            className={`px-3 py-1.5 rounded-full text-xs transition border backdrop-blur-sm text-left truncate max-w-[280px] sm:max-w-none ${
              language === 'ne' ? 'font-nepali' : ''
            } bg-slate-900/80 border-slate-800 text-slate-300 hover:border-blue-500/50 hover:text-white hover:bg-slate-850 disabled:opacity-50`}
          >
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-cyan-400 shrink-0" />
              {prompt}
            </span>
          </button>
        ))}
      </div>

      {/* Main Physical Mic Action Zone */}
      <div className="flex items-center gap-4 mt-1">
        {/* Type / Keyboard Fallback Button */}
        <button
          onClick={onOpenTextInput}
          title="Type your inquiry"
          className="flex items-center justify-center h-12 w-12 rounded-2xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 hover:bg-slate-850 transition shadow-lg"
        >
          <Keyboard className="w-5 h-5" />
        </button>

        {/* Primary Kiosk Microphone Button */}
        <div className="relative flex items-center justify-center">
          {/* Active ripple rings */}
          {isListening && (
            <>
              <motion.div
                animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
                className="absolute inset-0 rounded-full bg-cyan-500/30 -z-10"
              />
              <motion.div
                animate={{ scale: [1, 1.4, 1], opacity: [0.8, 0.1, 0.8] }}
                transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut', delay: 0.3 }}
                className="absolute inset-0 rounded-full bg-blue-500/40 -z-10"
              />
            </>
          )}

          <button
            onClick={isListening ? onStopListening : onStartListening}
            disabled={isBusy}
            className={`relative h-18 w-18 sm:h-20 sm:w-20 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-2xl border ${
              isListening
                ? 'bg-gradient-to-tr from-cyan-500 to-blue-600 border-cyan-300 text-white shadow-cyan-500/50 scale-105'
                : 'bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-700 border-blue-400/40 text-white hover:scale-105 hover:shadow-blue-500/40 hover:border-blue-400'
            } disabled:opacity-60`}
          >
            {isListening ? (
              <MicOff className="w-8 h-8 animate-pulse text-white" />
            ) : (
              <Mic className="w-8 h-8 text-white" />
            )}
          </button>
        </div>

        {/* Stop Speaking Button (visible during speech) */}
        {isSpeaking ? (
          <button
            onClick={onStopSpeaking}
            title="Stop speaking"
            className="flex items-center justify-center h-12 w-12 rounded-2xl bg-rose-950/80 border border-rose-800 text-rose-300 hover:text-white hover:bg-rose-900 transition shadow-lg animate-pulse"
          >
            <Square className="w-4 h-4 fill-current" />
          </button>
        ) : (
          <div className="w-12 h-12" /> // spacer to keep mic centered
        )}
      </div>

      {/* Button Label / Kiosk Hint */}
      <div className="text-center text-xs font-medium text-slate-400">
        {isListening ? (
          <span className="text-cyan-400 font-semibold animate-pulse">
            {language === 'ne' ? 'तपाईंको आवाज सुन्दैछ... बोल्नुहोस्' : 'Listening to your voice... Speak now'}
          </span>
        ) : isSpeaking ? (
          <span className="text-sky-300">
            {language === 'ne' ? 'AI बोल्दैछ · रोक्न बटन थिच्नुहोस्' : 'AI is speaking · Tap Stop to interrupt'}
          </span>
        ) : isBusy ? (
          <span className="text-purple-300">
            {language === 'ne' ? 'उत्तर तयार गर्दैछ...' : 'Processing your inquiry...'}
          </span>
        ) : (
          <span className="text-slate-400">
            {language === 'ne'
              ? 'बोल्नको लागि माइक थिच्नुहोस् वा तल लेख्नुहोस्'
              : 'Tap microphone to speak or choose a topic'}
          </span>
        )}
      </div>
    </div>
  );
};
