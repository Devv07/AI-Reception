import React, { useState } from 'react';
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  RotateCcw,
  ChevronUp,
  ChevronDown,
  LayoutGrid,
  Radio,
  ExternalLink,
  Sparkles,
  Zap,
  Columns,
  Monitor,
  LayoutDashboard,
} from 'lucide-react';
import { useDemoStore, demoStore, DEMO_STEPS } from '../../services/demoStore';

interface DemoControllerProps {
  currentPath?: string;
  onNavigate?: (path: string) => void;
  isSplitView?: boolean;
  onToggleSplitView?: () => void;
}

export const DemoController: React.FC<DemoControllerProps> = ({
  currentPath,
  onNavigate,
  isSplitView,
  onToggleSplitView,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [showAllSteps, setShowAllSteps] = useState(false);
  const demo = useDemoStore();

  const currentStepDef = DEMO_STEPS.find((s) => s.step === demo.currentStep);
  const progressPercent = Math.round((demo.currentStep / 12) * 100);

  return (
    <div className="fixed bottom-3 right-3 sm:right-4 z-50 flex flex-col items-end select-none max-w-[95vw] sm:max-w-lg">
      {/* Main Drawer Container */}
      <div className="w-full bg-slate-900/95 border border-cyan-500/40 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden transition-all duration-300">
        {/* Header Bar */}
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-between px-3.5 py-2.5 bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border-b border-slate-800 cursor-pointer text-xs"
        >
          <div className="flex items-center gap-2 font-bold text-slate-100">
            <span className="flex h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="tracking-wide">AI RECEPTION DEMO MODE</span>
            <span className="text-[10px] font-mono-code px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-600/40 text-cyan-300">
              12-Step Event Simulator
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-300">
              {demo.currentStep > 0 ? `Step ${demo.currentStep}/12` : 'Idle Ready'}
            </span>
            {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-slate-400" /> : <ChevronUp className="w-3.5 h-3.5 text-slate-400" />}
          </div>
        </div>

        {/* Expanded Drawer Content */}
        {isOpen && (
          <div className="p-3 space-y-3">
            {/* Active Step Indicator Banner */}
            <div className="p-2.5 rounded-xl bg-slate-950/90 border border-slate-800 flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                    {currentStepDef ? currentStepDef.title : 'Ready to Run Simulator'}
                  </span>
                </div>
                {currentStepDef && (
                  <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800/40">
                    {currentStepDef.badge}
                  </span>
                )}
              </div>

              <p className="text-[11px] text-slate-400 leading-snug">
                {currentStepDef
                  ? currentStepDef.description
                  : 'Click [▶ Auto-Play] or [Next Step] to simulate the complete 12-step visitor-to-admin lifecycle.'}
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className="bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-400 h-full transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            {/* Playback Control Bar */}
            <div className="flex items-center justify-between gap-1.5 flex-wrap">
              <div className="flex items-center gap-1">
                {/* Step Back */}
                <button
                  onClick={() => demoStore.prevStep()}
                  title="Previous Step"
                  className="p-1.5 sm:px-2.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-slate-200 text-xs flex items-center gap-1 transition"
                >
                  <SkipBack className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Prev</span>
                </button>

                {/* Auto Play / Pause */}
                {demo.isPlaying ? (
                  <button
                    onClick={() => demoStore.pauseAutoPlay()}
                    className="px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md transition"
                  >
                    <Pause className="w-3.5 h-3.5" />
                    <span>Pause</span>
                  </button>
                ) : (
                  <button
                    onClick={() => demoStore.startAutoPlay()}
                    className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>Auto-Play Flow</span>
                  </button>
                )}

                {/* Step Forward */}
                <button
                  onClick={() => demoStore.nextStep()}
                  title="Next Step"
                  className="p-1.5 sm:px-2.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-slate-200 text-xs flex items-center gap-1 transition"
                >
                  <span className="hidden sm:inline">Next</span>
                  <SkipForward className="w-3.5 h-3.5" />
                </button>

                {/* Speed toggle */}
                <button
                  onClick={() =>
                    demoStore.setSpeed(
                      demo.speed === 'normal' ? 'fast' : demo.speed === 'fast' ? 'slow' : 'normal'
                    )
                  }
                  className="px-2 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 text-[10px] font-mono-code hover:bg-slate-700 transition"
                  title="Simulation Speed"
                >
                  {demo.speed === 'fast' ? '⚡ 2x Speed' : demo.speed === 'slow' ? '🐢 Slow' : '⏱ 1x Speed'}
                </button>
              </div>

              {/* Reset Button */}
              <button
                onClick={() => demoStore.resetDemo()}
                title="Reset to pristine state"
                className="p-1.5 sm:px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white text-xs flex items-center gap-1 transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Reset</span>
              </button>
            </div>

            {/* Quick-Jump Step Selector (Collapsible grid of all 12 steps) */}
            <div>
              <button
                onClick={() => setShowAllSteps(!showAllSteps)}
                className="w-full py-1 text-[11px] font-medium text-slate-400 hover:text-cyan-300 flex items-center justify-between border-t border-slate-800/80 pt-2 transition"
              >
                <span className="flex items-center gap-1.5">
                  <LayoutGrid className="w-3 h-3 text-cyan-400" />
                  <span>Direct Step Jump (1 to 12)</span>
                </span>
                <span className="text-[10px] font-mono-code text-slate-500">
                  {showAllSteps ? 'Hide steps' : 'View all 12 steps'}
                </span>
              </button>

              {showAllSteps && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 pt-2 max-h-48 overflow-y-auto">
                  {DEMO_STEPS.map((s) => {
                    const isActive = demo.currentStep === s.step;
                    return (
                      <button
                        key={s.step}
                        onClick={() => demoStore.executeStep(s.step)}
                        className={`p-1.5 rounded-lg border text-left text-[10px] transition flex flex-col gap-0.5 ${
                          isActive
                            ? 'bg-blue-900/60 border-cyan-400 text-white font-bold shadow-sm'
                            : 'bg-slate-950/70 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
                        }`}
                      >
                        <span className="truncate">
                          {s.step}. {s.title}
                        </span>
                        <span className="text-[9px] text-slate-400 line-clamp-1">{s.badge}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Navigation & Presentation Split View Buttons */}
            {onNavigate && (
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between gap-1.5 text-[11px]">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => onNavigate('/reception')}
                    className={`px-2 py-1 rounded-lg border transition flex items-center gap-1 ${
                      currentPath === '/reception' && !isSplitView
                        ? 'bg-blue-600 text-white border-blue-500 font-semibold'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:text-white'
                    }`}
                  >
                    <Monitor className="w-3 h-3" />
                    <span>Public Kiosk</span>
                  </button>

                  <button
                    onClick={() => onNavigate('/dashboard/live')}
                    className={`px-2 py-1 rounded-lg border transition flex items-center gap-1 ${
                      currentPath?.startsWith('/dashboard') && !isSplitView
                        ? 'bg-blue-600 text-white border-blue-500 font-semibold'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:text-white'
                    }`}
                  >
                    <LayoutDashboard className="w-3 h-3" />
                    <span>Admin Telemetry</span>
                  </button>
                </div>

                {onToggleSplitView && (
                  <button
                    onClick={onToggleSplitView}
                    className={`px-2.5 py-1 rounded-lg border transition flex items-center gap-1.5 ${
                      isSplitView
                        ? 'bg-cyan-600 text-white border-cyan-400 font-bold shadow-md shadow-cyan-950'
                        : 'bg-slate-950 border-cyan-700/60 text-cyan-300 hover:bg-cyan-950/50'
                    }`}
                  >
                    <Columns className="w-3.5 h-3.5 text-cyan-300" />
                    <span>{isSplitView ? 'Split: ON' : 'Split View'}</span>
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
