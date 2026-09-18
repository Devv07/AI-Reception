import React, { useState } from 'react';
import { motion } from 'motion/react';
import { ReceiptText, CheckCircle2, AlertCircle, X } from 'lucide-react';
import { TicketData, LanguageMode } from '../../types/reception';

interface TicketCreationModalProps {
  language: LanguageMode;
  onConfirm: (data: TicketData) => void;
  onCancel: () => void;
}

export const TicketCreationModal: React.FC<TicketCreationModalProps> = ({
  language,
  onConfirm,
  onCancel,
}) => {
  const [issueSummary, setIssueSummary] = useState(
    'Admission fee transaction pending / Bank debit verification needed'
  );
  const [department, setDepartment] = useState('Admissions & Accounts');
  const [priority, setPriority] = useState<'Normal' | 'High'>('Normal');
  const [visitorName, setVisitorName] = useState('Ankit K.C.');
  const [contact, setContact] = useState('9812345678');
  const [isCreated, setIsCreated] = useState(false);
  const [createdTicket, setCreatedTicket] = useState<TicketData | null>(null);

  const handleCreate = () => {
    const randomId = `TCK-${Math.floor(2000 + Math.random() * 8000)}`;
    const ticket: TicketData = {
      ticketId: randomId,
      issueSummary,
      department,
      priority,
      visitorName,
      contact,
      status: 'Open',
      createdAt: new Date().toLocaleTimeString(),
    };
    setCreatedTicket(ticket);
    setIsCreated(true);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-xl mx-auto my-2 rounded-2xl bg-slate-900/95 border border-indigo-500/40 p-5 shadow-2xl shadow-indigo-500/10 backdrop-blur-xl z-30"
    >
      {!isCreated ? (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                <ReceiptText className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  {language === 'ne' ? 'सहायता अनुरोध टिकट सिर्जना' : 'Create Front Desk Service Ticket'}
                </h3>
                <p className="text-xs text-slate-400">
                  {language === 'ne'
                    ? 'तपाईंको समस्या सम्बन्धित शाखामा दर्ता गरिँदैछ'
                    : 'Dispatches issue directly to department queue'}
                </p>
              </div>
            </div>
            <button onClick={onCancel} className="p-1 rounded-md text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Issue Summary</label>
            <input
              type="text"
              value={issueSummary}
              onChange={(e) => setIssueSummary(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Assigned Department</label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                <option>Admissions & Accounts</option>
                <option>Examination Section</option>
                <option>Student Affairs</option>
                <option>IT Support</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Priority</label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPriority('Normal')}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium border transition ${
                    priority === 'Normal'
                      ? 'bg-blue-600 border-blue-400 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400'
                  }`}
                >
                  Normal
                </button>
                <button
                  type="button"
                  onClick={() => setPriority('High')}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium border transition ${
                    priority === 'High'
                      ? 'bg-amber-600 border-amber-400 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400'
                  }`}
                >
                  High
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Contact Name</label>
              <input
                type="text"
                value={visitorName}
                onChange={(e) => setVisitorName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Phone Number</label>
              <input
                type="text"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white border border-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 transition"
            >
              Generate Official Ticket
            </button>
          </div>
        </div>
      ) : (
        /* Confirmed Ticket State */
        <div className="flex flex-col items-center text-center gap-3 py-3">
          <div className="h-12 w-12 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 mb-1">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white">
            {language === 'ne' ? 'टिकट सिर्जना गरियो' : 'Service Ticket Generated'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm">
            Your inquiry has been assigned to the Admissions & Accounts queue. You may proceed to Counter A-102.
          </p>

          <div className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-left my-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
              <span className="text-slate-400">Ticket ID:</span>
              <span className="font-mono-code font-bold text-indigo-400 text-sm">
                {createdTicket?.ticketId}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-slate-300">
              <div>
                <span className="text-slate-500 block text-[11px]">Department:</span>
                <span className="font-semibold">{createdTicket?.department}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Priority / Status:</span>
                <span className="font-semibold text-emerald-400">
                  {createdTicket?.priority} · {createdTicket?.status}
                </span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-500 block text-[11px]">Summary:</span>
                <span>{createdTicket?.issueSummary}</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => createdTicket && onConfirm(createdTicket)}
            className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition"
          >
            Done & Return to Reception
          </button>
        </div>
      )}
    </motion.div>
  );
};
