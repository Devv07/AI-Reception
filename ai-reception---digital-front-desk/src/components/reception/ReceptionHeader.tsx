import React, { useEffect, useState } from 'react';
import { Volume2, VolumeX, ShieldCheck, Camera, Radio } from 'lucide-react';
import { LanguageMode } from '../../types/reception';
import { TCMIT_INFO } from '../../data/tcmitData';

interface ReceptionHeaderProps {
  language: LanguageMode;
  onLanguageChange: (lang: LanguageMode) => void;
  audioEnabled: boolean;
  onToggleAudio: () => void;
  sensorActive: boolean;
  onTriggerPresence?: () => void;
  onNavigateToDashboard?: () => void;
}

export const ReceptionHeader: React.FC<ReceptionHeaderProps> = ({
  language,
  onLanguageChange,
  audioEnabled,
  onToggleAudio,
  sensorActive,
  onTriggerPresence,
  onNavigateToDashboard,
}) => {
  const [timeString, setTimeString] = useState<string>('');
  const [dateString, setDateString] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeString(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: true,
        })
      );
      setDateString(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="w-full flex items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md z-30 select-none">
      {/* Organization Branding */}
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 via-blue-600 to-cyan-500 p-[1.5px] shadow-lg shadow-indigo-500/20">
          <div className="h-full w-full rounded-[10px] bg-slate-950 flex items-center justify-center">
            <span className="font-extrabold text-sm tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">
              TC
            </span>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
              {TCMIT_INFO.name}
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-medium">
                AI Front Desk
              </span>
            </h1>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">
            {language === 'ne' ? TCMIT_INFO.fullNameNe : TCMIT_INFO.fullName}
          </p>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="hidden lg:flex items-center gap-4 text-xs">
        {/* Proximity / Sensor Status */}
        <button
          onClick={onTriggerPresence}
          title="Click to toggle simulated sensor detection"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-300 hover:border-slate-700 transition"
        >
          <div className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                sensorActive ? 'bg-emerald-400' : 'bg-slate-500'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                sensorActive ? 'bg-emerald-500' : 'bg-slate-500'
              }`}
            />
          </div>
          <Camera className="w-3.5 h-3.5 text-slate-400" />
          <span>Presence Sensor: {sensorActive ? 'Visitor Detected' : 'Monitoring'}</span>
        </button>

        {/* Privacy Assurance Badge */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800/80 text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <span>Privacy Guaranteed · No Biometric Stored</span>
        </div>

        {/* Physical Kiosk Node */}
        <div className="flex items-center gap-1.5 text-slate-500 font-mono-code text-[11px]">
          <Radio className="w-3 h-3 text-indigo-400" />
          <span>{TCMIT_INFO.receptionKioskId}</span>
        </div>
      </div>

      {/* Right Controls: Time, Language & Audio */}
      <div className="flex items-center gap-3">
        {/* Time & Date Display */}
        <div className="text-right hidden sm:block">
          <div className="text-sm font-semibold text-slate-200 font-mono-code">{timeString}</div>
          <div className="text-[11px] text-slate-400">{dateString}</div>
        </div>

        <div className="h-6 w-px bg-slate-800 hidden sm:block" />

        {/* Language Switcher */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
          <button
            onClick={() => onLanguageChange('en')}
            className={`px-2.5 py-1 rounded-md font-medium transition ${
              language === 'en'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            English
          </button>
          <button
            onClick={() => onLanguageChange('ne')}
            className={`px-2.5 py-1 rounded-md font-nepali font-medium transition ${
              language === 'ne'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            नेपाली
          </button>
        </div>

        {/* Audio Mute/Unmute Toggle */}
        <button
          onClick={onToggleAudio}
          title={audioEnabled ? 'Voice output active' : 'Voice muted'}
          className={`p-2 rounded-lg border transition ${
            audioEnabled
              ? 'bg-slate-900 border-slate-700 text-cyan-400 hover:bg-slate-800'
              : 'bg-slate-900/50 border-slate-800 text-slate-500 hover:bg-slate-900'
          }`}
        >
          {audioEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>

        {/* Staff Dashboard Portal Link */}
        {onNavigateToDashboard && (
          <button
            onClick={onNavigateToDashboard}
            title="Open Staff Operations Dashboard"
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white text-xs font-medium transition"
          >
            <span>Staff Portal</span>
          </button>
        )}
      </div>
    </header>
  );
};
