import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  MessageSquare,
  Clock,
  BookOpen,
  ArrowRight,
  User,
  Bot,
  Terminal,
  UserCheck,
  X,
  ExternalLink,
  ChevronRight,
  Calendar,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { useDemoStore } from '../../services/demoStore';
import { LoadingState, EmptyState, ErrorState } from './StateViews';
import { ConversationItem } from '../../types/dashboard';

interface ConversationsViewProps {
  selectedId?: string | null;
  onSelectId?: (id: string | null) => void;
}

export const ConversationsView: React.FC<ConversationsViewProps> = ({ selectedId, onSelectId }) => {
  const demo = useDemoStore();
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');

  // Slide-over detail state
  const [activeConversation, setActiveConversation] = useState<ConversationItem | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchConversations = async () => {
    try {
      setError(null);
      const items = await DashboardService.getConversations(search, channelFilter);
      setConversations(items);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch conversations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [search, channelFilter, demo.conversations]);

  // Handle URL or external ID selection
  useEffect(() => {
    if (selectedId) {
      loadDetail(selectedId);
    } else {
      setActiveConversation(null);
    }
  }, [selectedId]);

  const loadDetail = async (id: string) => {
    try {
      setDetailLoading(true);
      const item = await DashboardService.getConversationDetail(id);
      setActiveConversation(item);
    } catch {
      setActiveConversation(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleOpenDetail = (item: ConversationItem) => {
    onSelectId?.(item.id);
    setActiveConversation(item);
  };

  const handleCloseDetail = () => {
    onSelectId?.(null);
    setActiveConversation(null);
  };

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">AI Reception Conversations</h2>
          <p className="text-xs text-slate-400">
            Recorded interactions between visitors and TCMIT digital receptionist
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
          {/* Search Bar */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search intent or query..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          {/* Channel Filter */}
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all">All Channels</option>
            <option value="reception">Reception Kiosk</option>
            <option value="phone">Phone Support</option>
          </select>
        </div>
      </div>

      {/* Main List */}
      {loading ? (
        <LoadingState message="Fetching conversation transcripts..." />
      ) : error ? (
        <ErrorState title="Conversations Error" error={error} onRetry={fetchConversations} />
      ) : conversations.length === 0 ? (
        <EmptyState
          title="No conversations match criteria"
          description="Try resetting your search query or channel filter."
          actionText="Reset Filters"
          onAction={() => {
            setSearch('');
            setChannelFilter('all');
          }}
        />
      ) : (
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 border-b border-slate-800 text-slate-400 font-mono-code text-[11px] uppercase">
                <tr>
                  <th className="p-3.5 pl-5">Visitor / ID</th>
                  <th className="p-3.5">Intent / Classification</th>
                  <th className="p-3.5">Channel</th>
                  <th className="p-3.5">Language</th>
                  <th className="p-3.5">Duration</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {conversations.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => handleOpenDetail(c)}
                    className="hover:bg-slate-800/40 transition cursor-pointer group"
                  >
                    <td className="p-3.5 pl-5">
                      <div className="font-semibold text-slate-100 group-hover:text-blue-300 transition">
                        {c.visitorName || c.visitorId}
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono-code">{c.visitorId}</span>
                    </td>
                    <td className="p-3.5">
                      <span className="font-medium text-slate-200 block">{c.intent}</span>
                      <span className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                        {c.actionTaken}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono-code text-slate-400">{c.channel}</td>
                    <td className="p-3.5">
                      <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-slate-800 text-cyan-300">
                        {c.language === 'ne' ? 'नेपाली' : 'English'}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono-code text-slate-400">{c.duration}</td>
                    <td className="p-3.5">
                      <span
                        className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full ${
                          c.status === 'Human handoff'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right pr-5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDetail(c);
                        }}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white transition"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Conversation Detail Slide-Over Modal (/dashboard/conversations/[id]) */}
      {activeConversation && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-xl h-full bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col justify-between overflow-hidden animate-in slide-in-from-right duration-200">
            {/* Modal Top Bar */}
            <div className="p-5 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-blue-400 font-mono-code">
                    SESSION #{activeConversation.id}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {activeConversation.channel}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mt-1">
                  {activeConversation.visitorName || activeConversation.visitorId}
                </h3>
              </div>

              <button
                onClick={handleCloseDetail}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Scrollable Body */}
            <div className="flex-1 p-5 overflow-y-auto space-y-4">
              {/* Metadata Badges */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Classified Intent:</span>
                  <strong className="text-cyan-300">{activeConversation.intent}</strong>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Status:</span>
                  <span
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full ${
                      activeConversation.status === 'Human handoff'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {activeConversation.status}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Recorded Duration:</span>
                  <span className="text-slate-300 font-mono-code">{activeConversation.duration}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Action Result:</span>
                  <span className="text-slate-200">{activeConversation.actionTaken}</span>
                </div>
              </div>

              {/* RAG Knowledge Grounding Sources */}
              {activeConversation.sourcesUsed.length > 0 && (
                <div className="p-3.5 rounded-xl bg-blue-950/30 border border-blue-800/40 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-blue-300">
                    <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                    <span>Retrieved Knowledge Evidence</span>
                  </div>
                  {activeConversation.sourcesUsed.map((src) => (
                    <div key={src.id} className="text-xs space-y-1">
                      <div className="flex items-center justify-between text-slate-300 font-medium">
                        <span>{src.document} (Page {src.page})</span>
                        <span className="text-[10px] font-mono-code text-cyan-400">
                          {Math.round(src.confidence * 100)}% Match
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 italic bg-slate-950/60 p-2 rounded border border-slate-800">
                        "{src.excerpt}"
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Messages Timeline */}
              <div className="space-y-3 pt-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Complete Interaction Log
                </span>

                {activeConversation.messages.map((m) => (
                  <div
                    key={m.id}
                    className={`flex flex-col gap-1 ${
                      m.sender === 'USER'
                        ? 'items-end'
                        : m.sender === 'STAFF'
                        ? 'items-center'
                        : m.sender === 'SYSTEM'
                        ? 'items-center'
                        : 'items-start'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono-code">
                      <span>{m.sender}</span>
                      <span>·</span>
                      <span>{m.timestamp}</span>
                    </div>

                    <div
                      className={`max-w-[85%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                        m.sender === 'USER'
                          ? 'bg-blue-600 text-white rounded-br-none'
                          : m.sender === 'STAFF'
                          ? 'bg-amber-950/80 border border-amber-600 text-amber-200 text-center'
                          : m.sender === 'SYSTEM'
                          ? 'bg-slate-950 border border-slate-800 text-slate-400 text-center text-[11px]'
                          : 'bg-slate-800 text-slate-100 rounded-bl-none border border-slate-700/60'
                      }`}
                    >
                      {m.text}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Modal Actions */}
            <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end">
              <button
                onClick={handleCloseDetail}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
              >
                Close Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
