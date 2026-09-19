import React from 'react';
import { motion } from 'motion/react';
import { ReceptionState } from '../../types/reception';
import { Mic, Sparkles, BrainCircuit, AudioWaveform, ArrowRightCircle } from 'lucide-react';

interface AIOrbProps {
  state: ReceptionState;
  onClick?: () => void;
}

export const AIOrb: React.FC<AIOrbProps> = ({ state, onClick }) => {
  // State specific colors, rings and animations
  const getStateConfig = () => {
    switch (state) {
      case 'IDLE':
        return {
          glowColor: 'rgba(59, 130, 246, 0.25)',
          coreGradient: 'from-blue-600 via-indigo-600 to-cyan-400',
          ringColor: 'border-blue-500/20',
          statusLabel: 'Reception Ready',
          statusBadgeClass: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
          icon: <Sparkles className="w-4 h-4 text-blue-400 animate-pulse" />,
        };
      case 'VISITOR_DETECTED':
        return {
          glowColor: 'rgba(16, 185, 129, 0.35)',
          coreGradient: 'from-emerald-500 via-teal-600 to-cyan-400',
          ringColor: 'border-emerald-500/30',
          statusLabel: 'Visitor Approaching · Initializing Greeting',
          statusBadgeClass: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
          icon: <Sparkles className="w-4 h-4 text-emerald-400" />,
        };
      case 'LISTENING':
        return {
          glowColor: 'rgba(6, 182, 212, 0.45)',
          coreGradient: 'from-cyan-500 via-blue-600 to-indigo-500',
          ringColor: 'border-cyan-400/40',
          statusLabel: 'Listening to your voice...',
          statusBadgeClass: 'text-cyan-300 border-cyan-400/40 bg-cyan-500/15 animate-pulse',
          icon: <Mic className="w-4 h-4 text-cyan-400" />,
        };
      case 'THINKING':
        return {
          glowColor: 'rgba(139, 92, 246, 0.4)',
          coreGradient: 'from-purple-600 via-indigo-600 to-blue-500',
          ringColor: 'border-purple-500/40',
          statusLabel: 'Retrieving Verified TCMIT Information...',
          statusBadgeClass: 'text-purple-300 border-purple-500/30 bg-purple-500/15',
          icon: <BrainCircuit className="w-4 h-4 text-purple-400 animate-spin" />,
        };
      case 'SPEAKING':
        return {
          glowColor: 'rgba(56, 189, 248, 0.45)',
          coreGradient: 'from-sky-400 via-blue-600 to-indigo-500',
          ringColor: 'border-sky-400/40',
          statusLabel: 'Speaking · TCMIT Voice Assistant',
          statusBadgeClass: 'text-sky-300 border-sky-400/40 bg-sky-500/15',
          icon: <AudioWaveform className="w-4 h-4 text-sky-400" />,
        };
      case 'HANDOFF':
        return {
          glowColor: 'rgba(245, 158, 11, 0.35)',
          coreGradient: 'from-amber-500 via-orange-600 to-yellow-500',
          ringColor: 'border-amber-500/30',
          statusLabel: 'Routing to Front Desk Staff...',
          statusBadgeClass: 'text-amber-300 border-amber-500/30 bg-amber-500/15',
          icon: <ArrowRightCircle className="w-4 h-4 text-amber-400 animate-bounce" />,
        };
      case 'ACTION_APPOINTMENT':
      case 'ACTION_TICKET':
      default:
        return {
          glowColor: 'rgba(99, 102, 241, 0.35)',
          coreGradient: 'from-indigo-500 via-blue-600 to-cyan-400',
          ringColor: 'border-indigo-500/30',
          statusLabel: 'Processing Service Request...',
          statusBadgeClass: 'text-indigo-300 border-indigo-500/30 bg-indigo-500/15',
          icon: <Sparkles className="w-4 h-4 text-indigo-400" />,
        };
    }
  };

  const config = getStateConfig();

  return (
    <div
      onClick={onClick}
      className="relative flex flex-col items-center justify-center my-4 cursor-pointer select-none group"
    >
      {/* Dynamic Ambient Background Glow */}
      <div
        className="absolute w-72 h-72 sm:w-80 sm:h-80 rounded-full blur-3xl transition-all duration-1000 -z-10 pointer-events-none"
        style={{ backgroundColor: config.glowColor }}
      />

      {/* Outer Concentric Animated Rings */}
      <div className="relative flex items-center justify-center w-52 h-52 sm:w-64 sm:h-64">
        {/* Ring 3: Outermost Acoustic Ring */}
        <motion.div
          animate={
            state === 'LISTENING'
              ? { scale: [1, 1.25, 1], opacity: [0.3, 0.7, 0.3] }
              : state === 'SPEAKING'
              ? { scale: [1, 1.15, 1], opacity: [0.25, 0.6, 0.25] }
              : state === 'THINKING'
              ? { rotate: 360 }
              : { scale: [1, 1.05, 1], opacity: [0.15, 0.3, 0.15] }
          }
          transition={{
            duration: state === 'THINKING' ? 8 : 4,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={`absolute inset-0 rounded-full border ${config.ringColor} transition-colors duration-700`}
        />

        {/* Ring 2: Intermediate Gyroscopic Ring */}
        <motion.div
          animate={
            state === 'LISTENING'
              ? { scale: [1, 1.18, 1], rotate: -180 }
              : state === 'SPEAKING'
              ? { scale: [1, 1.1, 1], rotate: 180 }
              : state === 'THINKING'
              ? { rotate: -360, scale: [0.95, 1.05, 0.95] }
              : { scale: [1, 1.04, 1], rotate: 90 }
          }
          transition={{
            duration: state === 'THINKING' ? 5 : 7,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={`absolute inset-4 rounded-full border border-dashed ${config.ringColor} transition-colors duration-700 opacity-60`}
        />

        {/* Ring 1: Inner Waveform Resonance Ring */}
        <motion.div
          animate={
            state === 'LISTENING'
              ? { scale: [1, 1.12, 1] }
              : state === 'SPEAKING'
              ? { scale: [0.98, 1.08, 0.98] }
              : state === 'VISITOR_DETECTED'
              ? { scale: [1, 1.15, 1] }
              : { scale: [1, 1.03, 1] }
          }
          transition={{
            duration: state === 'SPEAKING' ? 1.5 : 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute inset-8 rounded-full border border-slate-700/60 shadow-inner"
        />

        {/* Core Living Orb */}
        <motion.div
          animate={
            state === 'LISTENING'
              ? { scale: [1, 1.08, 1], filter: 'brightness(1.2)' }
              : state === 'SPEAKING'
              ? { scale: [0.96, 1.06, 0.96], filter: 'brightness(1.25)' }
              : state === 'THINKING'
              ? { rotate: 360, filter: 'hue-rotate(45deg)' }
              : { scale: [1, 1.03, 1] }
          }
          transition={{
            duration: state === 'THINKING' ? 3 : state === 'SPEAKING' ? 1.2 : 3.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={`relative w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-gradient-to-tr ${config.coreGradient} p-1 shadow-2xl shadow-blue-500/30 flex items-center justify-center transition-all duration-700`}
        >
          {/* Internal Refraction Sphere */}
          <div className="w-full h-full rounded-full bg-slate-950/40 backdrop-blur-sm flex items-center justify-center relative overflow-hidden border border-white/20">
            {/* Specular highlight crescent */}
            <div className="absolute top-2 left-3 w-10 h-6 rounded-full bg-white/25 blur-[3px] rotate-[-25deg] pointer-events-none" />

            {/* Speaking / Listening Frequency Bars Simulation */}
            {state === 'SPEAKING' ? (
              <div className="flex items-center gap-1 h-8 z-10">
                {[40, 75, 100, 60, 90, 45, 80, 50].map((h, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: [`${h * 0.25}%`, `${h}%`, `${h * 0.3}%`] }}
                    transition={{
                      duration: 0.6 + (i % 3) * 0.2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                      delay: i * 0.08,
                    }}
                    className="w-1 bg-white rounded-full opacity-90 shadow-sm"
                  />
                ))}
              </div>
            ) : state === 'LISTENING' ? (
              <div className="flex items-center gap-1 h-7 z-10">
                {[30, 60, 90, 100, 90, 60, 30].map((h, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: [`${h * 0.3}%`, `${h}%`, `${h * 0.2}%`] }}
                    transition={{
                      duration: 0.5 + (i % 2) * 0.2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                      delay: i * 0.05,
                    }}
                    className="w-1 bg-cyan-200 rounded-full"
                  />
                ))}
              </div>
            ) : (
              <div className="relative flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-white/80 blur-[1px] shadow-lg shadow-white" />
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Floating State Badge & Description */}
      <motion.div
        key={state}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mt-2 flex items-center gap-2"
      >
        <div
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-semibold backdrop-blur-md shadow-sm transition-all duration-500 ${config.statusBadgeClass}`}
        >
          {config.icon}
          <span>{config.statusLabel}</span>
        </div>
      </motion.div>
    </div>
  );
};
