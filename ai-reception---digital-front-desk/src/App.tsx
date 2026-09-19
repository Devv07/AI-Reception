import React, { useState, useEffect } from 'react';
import { PublicReceptionView } from './components/reception/PublicReceptionView';
import { DashboardShell } from './components/dashboard/DashboardShell';
import { OverviewView } from './components/dashboard/OverviewView';
import { LiveReceptionView } from './components/dashboard/LiveReceptionView';
import { ConversationsView } from './components/dashboard/ConversationsView';
import { VisitorsView } from './components/dashboard/VisitorsView';
import { AppointmentsView } from './components/dashboard/AppointmentsView';
import { TicketsView } from './components/dashboard/TicketsView';
import { KnowledgeView } from './components/dashboard/KnowledgeView';
import { DepartmentsView } from './components/dashboard/DepartmentsView';
import { AnalyticsView } from './components/dashboard/AnalyticsView';
import { SettingsView } from './components/dashboard/SettingsView';
import { Columns, Monitor, LayoutDashboard } from 'lucide-react';

export default function App() {
  const [currentPath, setCurrentPath] = useState<string>(() => {
    const path = window.location.pathname;
    if (path === '/' || path === '') return '/dashboard/live';
    return path;
  });

  const [isSplitView, setIsSplitView] = useState<boolean>(false);

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      setCurrentPath(path === '/' ? '/dashboard/live' : path);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (newPath: string) => {
    window.history.pushState({}, '', newPath);
    setCurrentPath(newPath);
  };

  const toggleSplitView = () => {
    setIsSplitView((prev) => !prev);
  };

  // Dashboard Page Content Router
  const renderDashboardContent = () => {
    if (currentPath === '/dashboard') {
      return <OverviewView onNavigate={navigate} />;
    } else if (currentPath === '/dashboard/live') {
      return <LiveReceptionView onNavigate={navigate} />;
    } else if (currentPath === '/dashboard/conversations') {
      return (
        <ConversationsView
          onSelectId={(id) =>
            navigate(id ? `/dashboard/conversations/${id}` : '/dashboard/conversations')
          }
        />
      );
    } else if (currentPath.startsWith('/dashboard/conversations/')) {
      const selectedId = currentPath.replace('/dashboard/conversations/', '');
      return (
        <ConversationsView
          selectedId={selectedId}
          onSelectId={(id) =>
            navigate(id ? `/dashboard/conversations/${id}` : '/dashboard/conversations')
          }
        />
      );
    } else if (currentPath === '/dashboard/visitors') {
      return <VisitorsView />;
    } else if (currentPath === '/dashboard/appointments') {
      return <AppointmentsView />;
    } else if (currentPath === '/dashboard/tickets') {
      return <TicketsView />;
    } else if (currentPath === '/dashboard/knowledge') {
      return <KnowledgeView />;
    } else if (currentPath === '/dashboard/departments') {
      return <DepartmentsView />;
    } else if (currentPath === '/dashboard/analytics') {
      return <AnalyticsView />;
    } else if (currentPath === '/dashboard/settings') {
      return <SettingsView />;
    }
    return <LiveReceptionView onNavigate={navigate} />;
  };

  // 1. Dual-Screen Split View (Hackathon Presentation Mode)
  if (isSplitView) {
    return (
      <div className="flex flex-col lg:flex-row h-screen w-screen overflow-hidden bg-slate-950">
        {/* Left Side: Physical AI Reception Kiosk Screen */}
        <div className="w-full lg:w-1/2 h-1/2 lg:h-full border-b lg:border-b-0 lg:border-r border-cyan-500/30 relative flex flex-col">
          <div className="absolute top-2 left-3 z-30 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/90 border border-cyan-500/40 text-[11px] text-cyan-300 font-mono-code backdrop-blur-md">
            <Monitor className="w-3.5 h-3.5" />
            <span>Physical Reception Screen (Kiosk A-01)</span>
          </div>
          <div className="flex-1 h-full overflow-hidden">
            <PublicReceptionView
              onNavigateToDashboard={() => navigate('/dashboard/live')}
              currentPath="/reception"
              onNavigate={navigate}
              isSplitView={isSplitView}
              onToggleSplitView={toggleSplitView}
            />
          </div>
        </div>

        {/* Right Side: Admin Operations Telemetry Dashboard */}
        <div className="w-full lg:w-1/2 h-1/2 lg:h-full relative flex flex-col">
          <DashboardShell
            currentPath={currentPath.startsWith('/dashboard') ? currentPath : '/dashboard/live'}
            onNavigate={navigate}
            isSplitView={isSplitView}
            onToggleSplitView={toggleSplitView}
          >
            {renderDashboardContent()}
          </DashboardShell>
        </div>
      </div>
    );
  }

  // 2. Physical AI Reception Screen Route: /reception
  if (currentPath === '/reception') {
    return (
      <PublicReceptionView
        onNavigateToDashboard={() => navigate('/dashboard/live')}
        currentPath="/reception"
        onNavigate={navigate}
        isSplitView={isSplitView}
        onToggleSplitView={toggleSplitView}
      />
    );
  }

  // 3. Admin Operations Dashboard Views
  return (
    <DashboardShell
      currentPath={currentPath}
      onNavigate={navigate}
      isSplitView={isSplitView}
      onToggleSplitView={toggleSplitView}
    >
      {renderDashboardContent()}
    </DashboardShell>
  );
}
