import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Send, X, Sparkles } from 'lucide-react';
import { LanguageMode } from '../../types/reception';

interface TextInputFallbackProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (text: string) => void;
  language: LanguageMode;
}

export const TextInputFallback: React.FC<TextInputFallbackProps> = ({
  isOpen,
  onClose,
  onSubmit,
  language,
}) => {
  const [inputText, setInputText] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSubmit(inputText.trim());
    setInputText('');
    onClose();
  };

  const sampleSuggestions =
    language === 'ne'
      ? [
          'BIT admission eligibility',
          'Principal भेट्ने समय',
          'शुल्क तिर्ने समस्या (Fee issue)',
          'Examination section कहाँ छ?',
        ]
      : [
          'BIT admission requirements and documents',
          "Book appointment with the Principal",
          'Admission payment failed report',
          'Where is the Accounts department?',
        ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="fixed inset-x-0 bottom-0 z-40 p-4 bg-slate-950/95 border-t border-slate-800 backdrop-blur-xl shadow-2xl"
    >
      <div className="max-w-2xl mx-auto flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-200 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            {language === 'ne' ? 'अनस्क्रिन टाइप गर्नुहोस्' : 'Type your question or request'}
          </span>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Input */}
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={
              language === 'ne'
                ? 'यहाँ लेख्नुहोस् (उदा: BIT admission को लागि के के चाहिन्छ?)...'
                : 'Type here (e.g. What are the BIT admission requirements?)...'
            }
            autoFocus
            className={`w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3 text-sm sm:text-base text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 pr-12 ${
              language === 'ne' ? 'font-nepali' : ''
            }`}
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="absolute right-2.5 h-9 w-9 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white flex items-center justify-center transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap gap-2 pt-1 text-xs">
          {sampleSuggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setInputText(s);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 transition truncate max-w-[240px]"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};
