import React from 'react';
import { motion } from 'motion/react';
import { ShieldCheck, UserCheck, RotateCcw, AlertCircle } from 'lucide-react';
import { LanguageMode } from '../../types/reception';

interface UnknownQuestionCardProps {
  language: LanguageMode;
  onConnectStaff: () => void;
  onAskSomethingElse: () => void;
}

export const UnknownQuestionCard: React.FC<UnknownQuestionCardProps> = ({
  language,
  onConnectStaff,
  onAskSomethingElse,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-xl mx-auto my-3 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-700/80 p-5 shadow-2xl shadow-black/50 backdrop-blur-xl z-30"
    >
      <div className="flex flex-col items-center text-center gap-3">
        {/* Trustworthy Icon */}
        <div className="h-12 w-12 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400">
          <ShieldCheck className="w-6 h-6 text-cyan-400" />
        </div>

        <div>
          <span className="text-[11px] font-mono-code px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            Responsible AI · Verified Knowledge Boundary
          </span>
          <h3 className="text-base sm:text-lg font-bold text-white mt-2">
            {language === 'ne'
              ? 'मलाई यो प्रश्नको जवाफ दिन पर्याप्त प्रमाणित जानकारी छैन।'
              : "I don't have enough verified information to answer that confidently."}
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-md">
            {language === 'ne'
              ? 'म तपाईंलाई हाम्रो रिसेप्सन शाखाका कर्मचारीसँग तुरुन्तै जोड्न सक्छु।'
              : 'I can connect you directly with a staff member to assist you with this.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 w-full justify-center pt-2">
          <button
            onClick={onConnectStaff}
            className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 transition flex items-center justify-center gap-2"
          >
            <UserCheck className="w-4 h-4" />
            <span>{language === 'ne' ? 'कर्मचारीसँग कुरा गर्नुहोस्' : 'Talk to Staff'}</span>
          </button>
          <button
            onClick={onAskSomethingElse}
            className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>{language === 'ne' ? 'अन्य विषय सोध्नुहोस्' : 'Ask Something Else'}</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};
