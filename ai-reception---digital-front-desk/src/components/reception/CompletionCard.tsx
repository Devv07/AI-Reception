import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, RotateCcw, ThumbsUp } from 'lucide-react';
import { LanguageMode } from '../../types/reception';

interface CompletionCardProps {
  language: LanguageMode;
  onAskAnother: () => void;
  onFinished: () => void;
}

export const CompletionCard: React.FC<CompletionCardProps> = ({
  language,
  onAskAnother,
  onFinished,
}) => {
  const [countdown, setCountdown] = useState(6);
  const [isGoodbye, setIsGoodbye] = useState(false);

  useEffect(() => {
    if (isGoodbye) {
      const timer = setInterval(() => {
        setCountdown((c) => {
          if (c <= 1) {
            clearInterval(timer);
            onFinished();
            return 0;
          }
          return c - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isGoodbye, onFinished]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="w-full max-w-lg mx-auto my-2 rounded-2xl bg-slate-900/90 border border-slate-800 p-5 text-center backdrop-blur-xl shadow-xl z-20"
    >
      {!isGoodbye ? (
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">
              {language === 'ne'
                ? 'के म तपाईंलाई अरू केही सहयोग गर्न सक्छु?'
                : 'Is there anything else I can help you with?'}
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              {language === 'ne'
                ? 'तपाईं अर्को प्रश्न सोध्न सक्नुहुन्छ वा सेवा अन्त्य गर्न सक्नुहुन्छ।'
                : 'You can ask another question or finish your visit.'}
            </p>
          </div>

          <div className="flex items-center gap-3 w-full justify-center pt-2">
            <button
              onClick={onAskAnother}
              className="flex-1 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{language === 'ne' ? 'हो, अर्को प्रश्न छ' : 'Yes, ask something else'}</span>
            </button>
            <button
              onClick={() => setIsGoodbye(true)}
              className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center justify-center gap-1.5"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
              <span>{language === 'ne' ? 'छैन, भयो / धन्यवाद' : "No, I'm all set"}</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 py-2">
          <div className="h-10 w-10 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <ThumbsUp className="w-5 h-5" />
          </div>
          <h4 className="text-lg font-bold text-white">
            {language === 'ne' ? 'TCMIT मा आउनुभएकोमा धन्यवाद!' : 'Thank you for visiting TCMIT!'}
          </h4>
          <p className="text-xs text-slate-300">
            {language === 'ne'
              ? 'तपाईंको दिन शुभ रहोस्।'
              : 'Have a wonderful day ahead. Returning to ambient reception...'}
          </p>
          <div className="mt-2 text-[11px] text-slate-500 font-mono-code">
            Resetting to ready state in {countdown}s
          </div>
        </div>
      )}
    </motion.div>
  );
};
