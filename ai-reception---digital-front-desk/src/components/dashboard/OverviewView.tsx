import React, { useState, useEffect } from 'react';
import {
  Users,
  MessageSquare,
  Calendar,
  Ticket,
  UserCheck,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Clock,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { LoadingState, ErrorState } from './StateViews';

interface OverviewViewProps {
  onNavigate: (route: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState<any>(null);
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setError(null);
      const [m, c] = await Promise.all([
        DashboardService.getOverviewMetrics(),
        DashboardService.getConversations(),
      ]);
      setMetrics(m);
      setConversations(c.slice(0, 4));
    } catch (err: any) {
      setError(err?.message || 'Failed to load dashboard overview');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Aggregating TCMIT operations metrics..." />;
  if (error) return <ErrorState title="Overview Error" error={error} onRetry={loadData} />;

  const metricCards = [
    {
      key: 'visitors',
      icon: Users,
      color: 'text-blue-400',
      bg: 'bg-blue-950/40 border-blue-800/50',
      route: '/dashboard/visitors',
      ...metrics.todayVisitors,
    },
    {
      key: 'conversations',
      icon: MessageSquare,
      color: 'text-cyan-400',
      bg: 'bg-cyan-950/40 border-cyan-800/50',
      route: '/dashboard/conversations',
      ...metrics.conversations,
    },
    {
      key: 'appointments',
      icon: Calendar,
      color: 'text-indigo-400',
      bg: 'bg-indigo-950/40 border-indigo-800/50',
      route: '/dashboard/appointments',
      ...metrics.appointments,
    },
    {
      key: 'tickets',
      icon: Ticket,
      color: 'text-purple-400',
      bg: 'bg-purple-950/40 border-purple-800/50',
      route: '/dashboard/tickets',
      ...metrics.openTickets,
    },
    {
      key: 'handoffs',
      icon: UserCheck,
      color: 'text-amber-400',
      bg: 'bg-amber-950/40 border-amber-800/50',
      route: '/dashboard/live',
      ...metrics.handoffs,
    },
  ];

  return (
    <div className="space-y-6 select-none pb-8">
      {/* Top Banner with Quick Live Reception Launch */}
      <div className="p-5 rounded-3xl bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-900 border border-blue-500/30 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono-code text-cyan-400">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>AI Operations Center · Live Kiosk Online</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">
            Tribhuvan College of Management & IT Reception Control
          </h2>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            Autonomous multi-lingual reception system handling visitor identification, admissions RAG consultation, appointment bookings, and staff escalations.
          </p>
        </div>

        <button
          onClick={() => onNavigate('/dashboard/live')}
          className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-xl shadow-blue-500/25 transition self-start md:self-auto hover:scale-105"
        >
          <Zap className="w-4 h-4" />
          <span>Open Live Kiosk Operations (/dashboard/live)</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* 5 Core Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {metricCards.map((m) => {
          const Icon = m.icon;
          return (
            <div
              key={m.key}
              onClick={() => onNavigate(m.route)}
              className={`p-4 rounded-2xl border ${m.bg} cursor-pointer hover:scale-[1.02] transition flex flex-col justify-between shadow-lg`}
            >
              <div className="flex items-center justify-between">
                <div className={`p-2 rounded-xl bg-slate-900/80 ${m.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono-code text-slate-400 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  {m.change}
                </span>
              </div>

              <div className="mt-3">
                <span className="text-2xl font-black text-white tracking-tight">{m.value}</span>
                <h4 className="text-xs font-semibold text-slate-200 mt-0.5">{m.title}</h4>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{m.subtext}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* 2-Column Split: Active System Health & Recent Conversations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Recent Activity Feed (7 cols) */}
        <div className="lg:col-span-7 rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-200">Recent AI Reception Sessions</h3>
              <p className="text-xs text-slate-400">Latest visitor queries and actions taken</p>
            </div>
            <button
              onClick={() => onNavigate('/dashboard/conversations')}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => onNavigate(`/dashboard/conversations/${c.id}`)}
                className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-blue-500/40 transition cursor-pointer flex items-center justify-between gap-3 group"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-blue-400 shrink-0">
                    <MessageSquare className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white group-hover:text-blue-300 transition">
                        {c.visitorName || c.visitorId}
                      </span>
                      <span className="text-[10px] font-mono-code px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        {c.channel}
                      </span>
                      <span className="text-[10px] font-mono-code text-cyan-400">
                        {c.language === 'ne' ? 'नेपाली' : 'English'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 font-medium">{c.intent}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{c.actionTaken}</p>
                  </div>
                </div>

                <div className="text-right shrink-0 flex flex-col items-end gap-1">
                  <span
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full ${
                      c.status === 'Human handoff'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {c.status}
                  </span>
                  <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono-code">
                    <Clock className="w-3 h-3" />
                    {c.startedAt}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Operational Health & Capabilities (5 cols) */}
        <div className="lg:col-span-5 rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-200">Kiosk Infrastructure Health</h3>
            <p className="text-xs text-slate-400">Real-time status of physical front-desk hardware</p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">Front Desk Presence Camera</span>
              <span className="text-emerald-400 font-mono-code font-bold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                Active (1.2m proximity)
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">Dual-Array Microphone</span>
              <span className="text-emerald-400 font-mono-code font-bold">Optimal SNR (32dB)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">TCMIT RAG Knowledge Index</span>
              <span className="text-cyan-400 font-mono-code font-bold">5 Documents (Synced)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">Staff Dispatch Webhook</span>
              <span className="text-emerald-400 font-mono-code font-bold">Online (0.12s latency)</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-blue-950/40 border border-blue-800/50 space-y-2">
            <span className="text-xs font-bold text-blue-300 block">Duty Staff Assignment</span>
            <p className="text-xs text-slate-300">
              Admissions Counter A-102: <strong className="text-white">Mr. Sunil Sharma</strong>
            </p>
            <p className="text-xs text-slate-300">
              Accounts Counter A-204: <strong className="text-white">Mrs. Sita Maharjan</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
