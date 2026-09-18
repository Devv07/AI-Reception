import React, { useState } from 'react';
import { Search, Users, Clock, MapPin, Radio } from 'lucide-react';
import { useDemoStore } from '../../services/demoStore';
import { EmptyState } from './StateViews';

export const VisitorsView: React.FC = () => {
  const demo = useDemoStore();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredVisitors = demo.visitors.filter((v) => {
    if (statusFilter !== 'all' && v.status.toLowerCase() !== statusFilter.toLowerCase()) {
      return false;
    }
    if (search) {
      const q = search.toLowerCase();
      return (
        v.code.toLowerCase().includes(q) ||
        v.purpose.toLowerCase().includes(q) ||
        v.department.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Top Header & Search Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Visitor Presence Logs</h2>
            <span className="text-xs font-mono-code px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-blue-300">
              {demo.visitors.length} Logged
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time tracking of visitors detected at TCMIT Lobby Reception Kiosk
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search visitor code or purpose..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all">All Statuses ({demo.visitors.length})</option>
            <option value="active">Active</option>
            <option value="needs staff">Needs Staff</option>
            <option value="departed">Departed</option>
          </select>
        </div>
      </div>

      {filteredVisitors.length === 0 ? (
        <EmptyState
          title="No visitors matched"
          description="Try modifying your search or status filter parameters."
          actionText="Reset Filters"
          onAction={() => {
            setSearch('');
            setStatusFilter('all');
          }}
        />
      ) : (
        <div className="overflow-x-auto rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono-code text-[11px]">
              <tr>
                <th className="py-3 px-4">Visitor Code</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Arrival & Duration</th>
                <th className="py-3 px-4">Inquiry / Purpose</th>
                <th className="py-3 px-4">Department & Counter</th>
                <th className="py-3 px-4">Channel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredVisitors.map((v) => (
                <tr key={v.id} className="hover:bg-slate-800/40 transition group">
                  <td className="py-3.5 px-4 font-mono-code font-bold text-white group-hover:text-cyan-400 transition">
                    {v.code}
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono-code font-bold uppercase ${
                        v.status === 'Active'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : v.status === 'Needs staff'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {v.status === 'Active' && (
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      )}
                      {v.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-slate-200 font-medium">{v.firstSeen}</span>
                      <span className="text-slate-400 text-[11px] flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {v.duration}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="text-slate-300 line-clamp-1">{v.purpose}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-slate-200 font-medium">{v.department}</span>
                      <span className="text-slate-400 text-[11px] flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        Last active: {v.lastInteraction}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-mono-code text-[11px] text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                      {v.channel}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
