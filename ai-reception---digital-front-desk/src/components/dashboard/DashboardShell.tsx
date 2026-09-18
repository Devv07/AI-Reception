import React, { useState } from 'react';
import {
  LayoutDashboard,
  Radio,
  MessageSquare,
  Users,
  Calendar,
  Ticket,
  BookOpen,
  Building2,
  BarChart3,
  Settings,
  Monitor,
  Menu,
  X,
  Bell,
  ExternalLink,
  Building,
  Columns,
} from 'lucide-react';
import { useDemoStore } from '../../services/demoStore';
import { DemoController } from '../reception/DemoController';

interface DashboardShellProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  isSplitView?: boolean;
  onToggleSplitView?: () => void;
  children: React.ReactNode;
}

export const DashboardShell: React.FC<DashboardShellProps> = ({
  currentPath,
  onNavigate,
  isSplitView,
  onToggleSplitView,
  children,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const demo = useDemoStore();

  const openTicketsCount = demo.tickets.filter((t) => t.status !== 'Resolved').length;
  const todayAppointmentsCount = demo.appointments.length;
  const hasHandoffAlert = demo.handoffAlert?.isActive;

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    {
      name: 'Live Reception',
      path: '/dashboard/live',
      icon: Radio,
      isLive: true,
      hasAlert: hasHandoffAlert,
    },
    { name: 'Conversations', path: '/dashboard/conversations', icon: MessageSquare },
    { name: 'Visitors', path: '/dashboard/visitors', icon: Users },
    {
      name: 'Appointments',
      path: '/dashboard/appointments',
      icon: Calendar,
      badgeCount: todayAppointmentsCount,
    },
    {
      name: 'Support Tickets',
      path: '/dashboard/tickets',
      icon: Ticket,
      badgeCount: openTicketsCount,
    },
    { name: 'Knowledge Base', path: '/dashboard/knowledge', icon: BookOpen },
    { name: 'Departments', path: '/dashboard/departments', icon: Building2 },
    { name: 'Analytics', path: '/dashboard/analytics', icon: BarChart3 },
    { name: 'Settings', path: '/dashboard/settings', icon: Settings },
  ];

  const handleNavClick = (path: string) => {
    onNavigate(path);
    setMobileMenuOpen(false);
  };

  const getPageTitle = () => {
    if (currentPath.startsWith('/dashboard/conversations/')) return 'Conversation Details';
    const found = navItems.find((n) => n.path === currentPath);
    return found ? found.name : 'Operations Dashboard';
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-slate-100 font-sans select-none">
      {/* 1. Desktop Left Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl shrink-0 z-30 justify-between">
        <div className="flex flex-col">
          {/* Logo & Institution Brand */}
          <div className="p-4 border-b border-slate-800/80 flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold">
              <Building className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xs font-black tracking-tight text-white uppercase font-mono-code">
                TCMIT Operations
              </h1>
              <p className="text-[10px] text-slate-400">AI Reception Control Center</p>
            </div>
          </div>

          {/* Quick Action: Kiosk Switcher Button */}
          <div className="p-3 space-y-2">
            <button
              onClick={() => onNavigate('/reception')}
              className="w-full flex items-center justify-between p-2.5 rounded-xl bg-gradient-to-r from-blue-900/40 to-indigo-900/40 hover:from-blue-800/50 hover:to-indigo-800/50 border border-blue-500/30 text-blue-300 hover:text-white transition group text-xs font-semibold shadow-lg shadow-blue-500/10"
            >
              <div className="flex items-center gap-2">
                <Monitor className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition" />
                <span>Physical Kiosk View</span>
              </div>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition" />
            </button>

            {onToggleSplitView && (
              <button
                onClick={onToggleSplitView}
                className={`w-full flex items-center justify-between p-2 rounded-xl text-xs font-medium border transition ${
                  isSplitView
                    ? 'bg-cyan-950 border-cyan-500/60 text-cyan-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Columns className="w-4 h-4 text-cyan-400" />
                  <span>Split Screen (Dual View)</span>
                </div>
                <span className="text-[10px] font-mono-code px-1.5 py-0.5 rounded bg-slate-800">
                  {isSplitView ? 'ON' : 'OFF'}
                </span>
              </button>
            )}
          </div>

          {/* Navigation Links */}
          <nav className="px-2 space-y-1 overflow-y-auto max-h-[calc(100vh-320px)]">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                currentPath === item.path ||
                (item.path === '/dashboard/conversations' &&
                  currentPath.startsWith('/dashboard/conversations/'));

              return (
                <button
                  key={item.path}
                  onClick={() => handleNavClick(item.path)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.name}</span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {item.hasAlert && (
                      <span className="flex items-center gap-1 text-[10px] font-bold font-mono-code px-1.5 py-0.5 rounded bg-amber-500 text-slate-950 animate-pulse">
                        <Bell className="w-2.5 h-2.5" />
                        ALERT
                      </span>
                    )}

                    {item.isLive && !item.hasAlert && (
                      <span className="flex items-center gap-1 text-[10px] font-mono-code px-1.5 py-0.2 rounded-full bg-rose-950 text-rose-300 border border-rose-800">
                        <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse" />
                        LIVE
                      </span>
                    )}

                    {item.badgeCount !== undefined && (
                      <span
                        className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full ${
                          isActive
                            ? 'bg-blue-700 text-white'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {item.badgeCount}
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom User / Duty Officer Card */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
          <div className="flex items-center gap-2.5 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="h-8 w-8 rounded-lg bg-blue-600/30 border border-blue-500/30 flex items-center justify-center text-blue-300 text-xs font-bold">
              SS
            </div>
            <div className="overflow-hidden">
              <span className="text-xs font-bold text-slate-200 block truncate">Sunil Sharma</span>
              <span className="text-[10px] text-slate-500 block truncate">
                Duty Officer · Counter A-102
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Operational Bar */}
        <header className="h-14 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-20">
          <div className="flex items-center gap-3">
            {/* Mobile Hamburger */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 md:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Breadcrumb / Title */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-500 hidden sm:inline">TCMIT Operations</span>
              <span className="text-slate-600 hidden sm:inline">/</span>
              <h2 className="text-sm font-bold text-white tracking-tight">{getPageTitle()}</h2>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Terminal status badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono-code text-slate-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>KIOSK-LOBBY-01: Online</span>
            </div>

            {/* Split Screen Toggle */}
            {onToggleSplitView && (
              <button
                onClick={onToggleSplitView}
                className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold transition ${
                  isSplitView
                    ? 'bg-cyan-600 text-white border-cyan-400 shadow-md shadow-cyan-900'
                    : 'bg-slate-900 border-slate-700 text-cyan-300 hover:bg-slate-800'
                }`}
              >
                <Columns className="w-3.5 h-3.5" />
                <span>{isSplitView ? 'Exit Split' : 'Dual Screen'}</span>
              </button>
            )}

            {/* Switch to Kiosk button */}
            <button
              onClick={() => onNavigate('/reception')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 hover:text-white text-xs font-semibold transition"
            >
              <Monitor className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Public Kiosk</span>
            </button>
          </div>
        </header>

        {/* Scrollable View Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-950 relative">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_-10%,rgba(30,58,138,0.15),transparent)] pointer-events-none" />
          <div className="max-w-7xl mx-auto relative z-10">{children}</div>
        </main>
      </div>

      {/* Floating Demo Controller */}
      <DemoController
        currentPath={currentPath}
        onNavigate={onNavigate}
        isSplitView={isSplitView}
        onToggleSplitView={onToggleSplitView}
      />

      {/* 3. Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex bg-slate-950/80 backdrop-blur-sm md:hidden">
          <div className="w-64 h-full bg-slate-900 border-r border-slate-800 p-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-black uppercase text-white font-mono-code">
                  TCMIT Operations
                </span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-1">
                {navItems.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => handleNavClick(item.path)}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
                  >
                    <span>{item.name}</span>
                    {item.badgeCount !== undefined && (
                      <span className="text-[10px] font-mono-code px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                        {item.badgeCount}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2 pt-4 border-t border-slate-800">
              <button
                onClick={() => handleNavClick('/reception')}
                className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs"
              >
                Go to Public Reception Kiosk
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
