import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Building2, MapPin, Clock, Phone, User, X, Navigation, CheckCircle2 } from 'lucide-react';
import { DEPARTMENTS } from '../../data/tcmitData';
import { DepartmentInfo, LanguageMode } from '../../types/reception';

interface DepartmentDirectoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  language: LanguageMode;
  onSelectDepartment?: (dept: DepartmentInfo) => void;
}

export const DepartmentDirectoryModal: React.FC<DepartmentDirectoryModalProps> = ({
  isOpen,
  onClose,
  language,
  onSelectDepartment,
}) => {
  const [activeDirection, setActiveDirection] = useState<DepartmentInfo | null>(null);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md select-none"
    >
      <div className="relative w-full max-w-3xl max-h-[85vh] overflow-hidden rounded-3xl bg-slate-900 border border-slate-700 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">
                {language === 'ne' ? 'TCMIT क्याम्पस शाखा निर्देशिका' : 'TCMIT Campus Directory & Locations'}
              </h3>
              <p className="text-xs text-slate-400">
                {language === 'ne'
                  ? 'शाखाहरू, कोठा नम्बर र सम्पर्क अधिकारीहरूको सूची'
                  : 'Floor locations, operating hours and duty officers'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Directory Grid */}
        <div className="p-6 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {DEPARTMENTS.map((dept) => (
            <div
              key={dept.id}
              className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/90 hover:border-blue-500/40 transition group flex flex-col justify-between gap-3"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold text-slate-100 group-hover:text-blue-300 transition">
                    {language === 'ne' ? dept.nameNe : dept.name}
                  </h4>
                  <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800/50 text-blue-400">
                    {dept.code}
                  </span>
                </div>

                <div className="mt-2 space-y-1.5 text-xs text-slate-300">
                  <div className="flex items-center gap-2 text-cyan-300">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span>
                      {dept.floor} · {dept.block} ({dept.room})
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{dept.hours}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <User className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>Duty: {dept.officer}</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-500 font-mono-code text-[11px] flex items-center gap-1">
                  <Phone className="w-3 h-3 text-slate-500" />
                  {dept.contact}
                </span>
                <button
                  onClick={() => setActiveDirection(dept)}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-300 hover:bg-blue-600 hover:text-white transition font-medium"
                >
                  <Navigation className="w-3 h-3" />
                  <span>Directions</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Direction Wayfinding Overlay */}
        {activeDirection && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-slate-950 border-t border-slate-800 text-xs flex items-center justify-between gap-4"
          >
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Navigation className="w-4 h-4" />
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">
                  Walking Guide from Main Reception:
                </span>
                <span className="font-semibold text-white">
                  Head straight through Lobby Corridor → Take Elevators/Stairs to {activeDirection.floor} of{' '}
                  {activeDirection.block} → Proceed to {activeDirection.room}
                </span>
              </div>
            </div>
            <button
              onClick={() => setActiveDirection(null)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white shrink-0"
            >
              Close Guide
            </button>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
