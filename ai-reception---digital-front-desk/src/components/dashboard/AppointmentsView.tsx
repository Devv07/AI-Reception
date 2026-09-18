import React, { useState } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  User,
  Building,
  CheckCircle2,
  XCircle,
  Clock3,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { useDemoStore } from '../../services/demoStore';
import { EmptyState } from './StateViews';
import { AppointmentRecord } from '../../types/dashboard';

export const AppointmentsView: React.FC = () => {
  const demo = useDemoStore();
  const [filter, setFilter] = useState('all');

  const filteredAppointments = demo.appointments.filter((a) => {
    if (filter === 'all') return true;
    return a.status.toLowerCase() === filter.toLowerCase();
  });

  const handleUpdateStatus = async (id: string, newStatus: AppointmentRecord['status']) => {
    await DashboardService.updateAppointmentStatus(id, newStatus);
  };

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Executive & Faculty Appointments</h2>
            <span className="text-xs font-mono-code px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-blue-300">
              {demo.appointments.length} Total
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Synchronized live with physical AI Reception Kiosk A-01
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all">All Appointments ({demo.appointments.length})</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {filteredAppointments.length === 0 ? (
        <EmptyState
          title="No appointments found"
          description="There are currently no visitor appointments matching this filter."
          actionText="Show All"
          onAction={() => setFilter('all')}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {filteredAppointments.map((a) => (
            <div
              key={a.id}
              className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl hover:border-slate-700/80 transition flex flex-col justify-between gap-3 group"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono-code text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    {a.id}
                  </span>
                  <span
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full uppercase font-bold flex items-center gap-1 ${
                      a.status === 'Confirmed'
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                        : a.status === 'Pending'
                        ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                        : a.status === 'Completed'
                        ? 'bg-blue-950/80 text-blue-300 border border-blue-800/60'
                        : 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                    }`}
                  >
                    {a.status === 'Confirmed' && <CheckCircle2 className="w-3 h-3" />}
                    {a.status === 'Pending' && <Clock3 className="w-3 h-3" />}
                    {a.status === 'Cancelled' && <XCircle className="w-3 h-3" />}
                    <span>{a.status}</span>
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition">
                    {a.visitorName}
                  </h3>
                  <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <User className="w-3 h-3 text-slate-500" />
                    <span>Meeting: <strong>{a.targetPerson}</strong> ({a.department})</span>
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 text-xs">
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      <CalendarIcon className="w-3 h-3" />
                      Date:
                    </span>
                    <strong className="font-mono-code">{a.date}</strong>
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Time:
                    </span>
                    <strong className="font-mono-code">{a.timeSlot}</strong>
                  </div>
                </div>

                <p className="text-xs text-slate-400 line-clamp-2 italic">"{a.purpose}"</p>
              </div>

              {/* Status Update Quick Action */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[10px] text-slate-500 font-mono-code">
                  Created {a.createdAt}
                </span>

                <div className="flex items-center gap-1.5">
                  {a.status === 'Pending' && (
                    <button
                      onClick={() => handleUpdateStatus(a.id, 'Confirmed')}
                      className="px-2.5 py-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-[11px] font-semibold transition"
                    >
                      Confirm
                    </button>
                  )}
                  {a.status === 'Confirmed' && (
                    <button
                      onClick={() => handleUpdateStatus(a.id, 'Completed')}
                      className="px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 text-[11px] font-semibold transition"
                    >
                      Complete
                    </button>
                  )}
                  {a.status !== 'Cancelled' && a.status !== 'Completed' && (
                    <button
                      onClick={() => handleUpdateStatus(a.id, 'Cancelled')}
                      className="px-2 py-1 rounded-lg text-slate-500 hover:text-rose-400 text-[11px] transition"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
