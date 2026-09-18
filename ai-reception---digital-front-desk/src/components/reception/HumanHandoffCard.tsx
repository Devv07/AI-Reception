import React from 'react';
import { motion } from 'motion/react';
import { UserCheck, ArrowRight, MapPin, Phone, CheckCircle, ShieldAlert } from 'lucide-react';
import { LanguageMode } from '../../types/reception';
import { DEPARTMENTS } from '../../data/tcmitData';

interface HumanHandoffCardProps {
  language: LanguageMode;
  onDone: () => void;
}

export const HumanHandoffCard: React.FC<HumanHandoffCardProps> = ({ language, onDone }) => {
  const admissionsDept = DEPARTMENTS[0];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-xl mx-auto my-2 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-amber-500/40 p-5 shadow-2xl shadow-amber-500/10 backdrop-blur-xl z-30"
    >
      <div className="flex flex-col items-center text-center gap-3">
        {/* Animated Beacon Wave AI -> Staff */}
        <div className="relative flex items-center justify-center my-1">
          <div className="h-14 w-14 rounded-full bg-amber-500/20 border border-amber-400/40 flex items-center justify-center text-amber-400">
            <UserCheck className="w-7 h-7 animate-pulse" />
          </div>
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500" />
          </span>
        </div>

        <div>
          <span className="text-[11px] font-mono-code font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-300">
            {language === 'ne' ? 'कर्मचारी हस्तान्तरण अनुरोध' : 'Staff Handoff Dispatched'}
          </span>
          <h3 className="text-lg font-bold text-white mt-1.5">
            {language === 'ne'
              ? 'ड्युटी कर्मचारीसँग जोडिँदैछ'
              : 'Connecting to On-Duty Front Desk Officer'}
          </h3>
          <p className="text-xs text-slate-300 mt-1 max-w-md">
            {language === 'ne'
              ? 'तपाईंको अनुरोध भर्ना शाखाको कर्मचारी टर्मिनलमा पठाइएको छ। कृपया तलको काउन्टरमा सम्पर्क गर्नुहोस् वा केही समय पर्खनुहोस्।'
              : 'A live alert has been beamed to the staff dashboard. An officer has been notified to assist you.'}
          </p>
        </div>

        {/* Assigned Officer & Counter Location */}
        <div className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 text-left text-xs my-1">
          <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2 mb-2">
            <span>Destination Desk:</span>
            <span className="font-semibold text-white flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-amber-400" />
              {admissionsDept.room} · {admissionsDept.block} ({admissionsDept.floor})
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-slate-300">
            <div>
              <span className="text-slate-500 block text-[10px]">Duty Officer:</span>
              <span className="font-medium text-slate-200">{admissionsDept.officer}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Estimated Wait:</span>
              <span className="font-medium text-emerald-400">Officer Notified (Immediate)</span>
            </div>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 text-xs text-amber-300 bg-amber-950/40 border border-amber-800/40 px-3 py-1.5 rounded-lg w-full justify-center">
          <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
          <span>Front Desk Terminal Status: Active · Staff Alert Sent</span>
        </div>

        <button
          onClick={onDone}
          className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition mt-1"
        >
          {language === 'ne' ? 'सम्पन्न भयो / रिसेप्सनमा फर्कनुहोस्' : 'Done · Return to AI Reception'}
        </button>
      </div>
    </motion.div>
  );
};
