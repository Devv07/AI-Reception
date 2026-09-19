import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Calendar, Clock, CheckCircle2, User, Phone, FileText, ArrowRight, X } from 'lucide-react';
import { AppointmentData, LanguageMode } from '../../types/reception';

interface AppointmentBookingModalProps {
  language: LanguageMode;
  onConfirm: (data: AppointmentData) => void;
  onCancel: () => void;
}

export const AppointmentBookingModal: React.FC<AppointmentBookingModalProps> = ({
  language,
  onConfirm,
  onCancel,
}) => {
  const [selectedDate, setSelectedDate] = useState('Tomorrow (Sep 19, 2026)');
  const [selectedTime, setSelectedTime] = useState('11:00 AM');
  const [visitorName, setVisitorName] = useState('Ram Prasad Sharma');
  const [contact, setContact] = useState('9841234567');
  const [purpose, setPurpose] = useState('BIT Admission Consultation & Credit Transfer Inquiry');
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [confirmedData, setConfirmedData] = useState<AppointmentData | null>(null);

  const timeSlots = ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '1:00 PM'];
  const dates = [
    'Today (Sep 18, 2026)',
    'Tomorrow (Sep 19, 2026)',
    'Sunday (Sep 21, 2026)',
  ];

  const handleBooking = () => {
    const randomRef = `APT-${Math.floor(1000 + Math.random() * 9000)}`;
    const record: AppointmentData = {
      department: "Principal's Executive Office",
      targetPerson: 'Prof. Dr. Rajendra Karki (Principal)',
      date: selectedDate,
      timeSlot: selectedTime,
      visitorName: visitorName || 'Anonymous Visitor',
      contact: contact || '+977-9800000000',
      purpose: purpose || 'General Consultation',
      referenceCode: randomRef,
      createdAt: new Date().toLocaleTimeString(),
    };
    setConfirmedData(record);
    setIsConfirmed(true);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-xl mx-auto my-2 rounded-2xl bg-slate-900/95 border border-blue-500/40 p-5 shadow-2xl shadow-blue-500/10 backdrop-blur-xl z-30"
    >
      {!isConfirmed ? (
        <div className="flex flex-col gap-4">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
                <Calendar className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  {language === 'ne' ? 'प्रिन्सिपलसँग भेटघाट समय तालिका' : "Principal's Office Appointment"}
                </h3>
                <p className="text-xs text-slate-400">Block B · 2nd Floor · Room B-201</p>
              </div>
            </div>
            <button onClick={onCancel} className="p-1 rounded-md text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Date Selector */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Select Preferred Date
            </label>
            <div className="grid grid-cols-3 gap-2">
              {dates.map((d) => (
                <button
                  key={d}
                  onClick={() => setSelectedDate(d)}
                  className={`p-2 rounded-xl text-xs font-medium border text-center transition ${
                    selectedDate === d
                      ? 'bg-blue-600 border-blue-400 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Time Slot Cards */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              Available Time Slots
            </label>
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
              {timeSlots.map((time) => (
                <button
                  key={time}
                  onClick={() => setSelectedTime(time)}
                  className={`py-2 px-1 rounded-xl text-xs font-mono-code font-medium border text-center transition ${
                    selectedTime === time
                      ? 'bg-blue-600 border-blue-400 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  {time}
                </button>
              ))}
            </div>
          </div>

          {/* Visitor Details Input */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div>
              <label className="text-xs text-slate-400 block mb-1 flex items-center gap-1">
                <User className="w-3 h-3 text-slate-400" /> Visitor Full Name
              </label>
              <input
                type="text"
                value={visitorName}
                onChange={(e) => setVisitorName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1 flex items-center gap-1">
                <Phone className="w-3 h-3 text-slate-400" /> Contact Phone
              </label>
              <input
                type="text"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Purpose */}
          <div>
            <label className="text-xs text-slate-400 block mb-1 flex items-center gap-1">
              <FileText className="w-3 h-3 text-slate-400" /> Purpose of Meeting
            </label>
            <input
              type="text"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white border border-slate-800 hover:bg-slate-850 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleBooking}
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg shadow-blue-500/25 transition"
            >
              <span>Confirm Appointment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      ) : (
        /* Confirmed State */
        <div className="flex flex-col items-center text-center gap-3 py-3">
          <div className="h-12 w-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mb-1">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white">
            {language === 'ne' ? 'भेटघाट निश्चित गरियो' : 'Appointment Confirmed'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm">
            Your appointment has been registered with the Principal's Executive Secretary. A notification slip has been issued.
          </p>

          {/* Appointment Ticket Slip */}
          <div className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-left my-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2.5">
              <span className="text-slate-400">Reference ID:</span>
              <span className="font-mono-code font-bold text-cyan-400 text-sm">
                {confirmedData?.referenceCode}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-slate-300">
              <div>
                <span className="text-slate-500 block text-[11px]">Person/Office:</span>
                <span className="font-semibold">{confirmedData?.targetPerson}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Date & Time:</span>
                <span className="font-semibold text-emerald-400">
                  {confirmedData?.date} · {confirmedData?.timeSlot}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Visitor Name:</span>
                <span>{confirmedData?.visitorName}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Location:</span>
                <span>Block B · Room B-201</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 mt-2 w-full">
            <button
              onClick={() => confirmedData && onConfirm(confirmedData)}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition"
            >
              Done & Return to Reception
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
};
