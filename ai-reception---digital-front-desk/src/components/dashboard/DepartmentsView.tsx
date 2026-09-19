import React, { useState, useEffect } from 'react';
import {
  Building2,
  MapPin,
  Clock,
  Phone,
  User,
  ShieldCheck,
  Search,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { LoadingState, EmptyState, ErrorState } from './StateViews';
import { DepartmentInfo } from '../../types/reception';

export const DepartmentsView: React.FC = () => {
  const [departments, setDepartments] = useState<DepartmentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchDepts = async () => {
    try {
      setLoading(true);
      setError(null);
      const items = await DashboardService.getDepartments();
      setDepartments(items);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch campus departments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDepts();
  }, []);

  const filtered = departments.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.code.toLowerCase().includes(search.toLowerCase()) ||
      d.officer.toLowerCase().includes(search.toLowerCase()) ||
      d.block.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4 select-none pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Campus Department Directory</h2>
          <p className="text-xs text-slate-400">
            Official department locations, operational hours, and duty personnel at TCMIT
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search department or officer..."
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading department configurations..." />
      ) : error ? (
        <ErrorState title="Departments Error" error={error} onRetry={fetchDepts} />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No departments found"
          description="No campus departments match your search term."
          actionText="Clear Search"
          onAction={() => setSearch('')}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {filtered.map((dept) => (
            <div
              key={dept.id}
              className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800/90 hover:border-blue-500/40 transition flex flex-col justify-between gap-3 shadow-lg"
            >
              <div>
                <div className="flex items-start justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                  <div>
                    <h3 className="text-sm font-bold text-white">{dept.name}</h3>
                    <span className="text-[11px] text-slate-400">{dept.nameNe}</span>
                  </div>
                  <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-blue-950 border border-blue-800 text-blue-300">
                    {dept.code}
                  </span>
                </div>

                <div className="mt-3 space-y-2 text-xs">
                  <div className="flex items-center gap-2 text-cyan-300 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span>
                      {dept.floor} · {dept.block} ({dept.room})
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300">
                    <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{dept.hours}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300">
                    <User className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>Duty Officer: {dept.officer}</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1 font-mono-code text-[11px]">
                  <Phone className="w-3 h-3 text-slate-500" />
                  {dept.contact}
                </span>
                <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2 py-0.5 rounded">
                  Open Today
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
