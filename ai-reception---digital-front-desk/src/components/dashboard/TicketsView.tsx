import React, { useEffect, useState } from 'react';
import {
  Ticket as TicketIcon,
  AlertCircle,
  CheckCircle2,
  Clock,
  User,
  Building,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { EmptyState, ErrorState, LoadingState } from './StateViews';
import { TicketRecord } from '../../types/dashboard';

export const TicketsView: React.FC = () => {
  const [tickets, setTickets] = useState<TicketRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  const loadTickets = async () => {
    try {
      setLoading(true);
      setError(null);
      setTickets(await DashboardService.getTickets());
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTickets(); }, []);

  const filteredTickets = tickets.filter((t) => {
    if (filter === 'all') return true;
    return t.status.toLowerCase() === filter.toLowerCase();
  });

  const handleUpdateStatus = async (id: string, newStatus: TicketRecord['status']) => {
    await DashboardService.updateTicketStatus(id, newStatus);
    await loadTickets();
  };

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Front-Desk Support Tickets</h2>
            <span className="text-xs font-mono-code px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-blue-300">
              {tickets.length} Active Tickets
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Escalations generated automatically by AI Receptionist for campus departments
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all">All Statuses ({tickets.length})</option>
            <option value="open">Open</option>
            <option value="in progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {loading ? <LoadingState message="Loading support tickets..." /> : error ? <ErrorState title="Tickets Error" error={error} onRetry={loadTickets} /> : filteredTickets.length === 0 ? (
        <EmptyState
          title="No tickets found"
          description="There are currently no tickets matching this filter."
          actionText="Show All"
          onAction={() => setFilter('all')}
        />
      ) : (
        <div className="space-y-3">
          {filteredTickets.map((t) => (
            <div
              key={t.id}
              className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl hover:border-slate-700/80 transition flex flex-col md:flex-row md:items-center justify-between gap-4 group"
            >
              <div className="space-y-1.5 max-w-2xl">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono-code font-bold text-cyan-400 bg-slate-950 px-2.5 py-0.5 rounded border border-slate-800">
                    {t.id}
                  </span>
                  <span
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full uppercase font-bold ${
                      t.priority === 'High'
                        ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                        : t.priority === 'Normal'
                        ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {t.priority} Priority
                  </span>
                  <span
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full uppercase font-bold flex items-center gap-1 ${
                      t.status === 'Resolved'
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                        : t.status === 'In Progress'
                        ? 'bg-blue-950/80 text-blue-300 border border-blue-800/60'
                        : 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                    }`}
                  >
                    {t.status === 'Resolved' && <CheckCircle2 className="w-3 h-3" />}
                    {t.status === 'In Progress' && <Clock className="w-3 h-3" />}
                    {t.status === 'Open' && <AlertCircle className="w-3 h-3" />}
                    <span>{t.status}</span>
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition">
                  {t.issue}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Assigned Staff: <span className="text-slate-300">{t.assignedStaff}</span>
                </p>

                <div className="flex items-center gap-4 text-xs text-slate-400 flex-wrap pt-1">
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3 text-slate-500" />
                    <span>Requester: <strong className="text-slate-200">{t.visitorName}</strong> ({t.contact})</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Building className="w-3 h-3 text-slate-500" />
                    <span>Assigned: <strong className="text-slate-200">{t.department}</strong></span>
                  </span>
                  <span className="font-mono-code text-[11px] text-slate-500">
                    Logged: {t.createdAt}
                  </span>
                </div>
              </div>

              {/* Status Action Buttons */}
              <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                {t.status === 'Open' && (
                  <button
                    onClick={() => handleUpdateStatus(t.id, 'In Progress')}
                    className="px-3 py-1.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 text-xs font-semibold transition"
                  >
                    Mark In Progress
                  </button>
                )}
                {t.status === 'In Progress' && (
                  <button
                    onClick={() => handleUpdateStatus(t.id, 'Resolved')}
                    className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition"
                  >
                    Resolve Ticket
                  </button>
                )}
                {t.status === 'Resolved' && (
                  <button
                    onClick={() => handleUpdateStatus(t.id, 'Open')}
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
                  >
                    Reopen
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
