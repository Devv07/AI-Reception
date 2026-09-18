import React from 'react';
import { AlertCircle, RefreshCw, Inbox, Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Loading operations data...' }) => (
  <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
    <div className="relative flex items-center justify-center">
      <div className="w-12 h-12 rounded-full border-2 border-slate-800 border-t-blue-500 animate-spin" />
      <div className="absolute w-6 h-6 rounded-full bg-blue-500/20 blur-sm animate-pulse" />
    </div>
    <span className="mt-4 text-sm font-medium text-slate-400">{message}</span>
  </div>
);

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'There is currently no data to display for this view or filter.',
  actionText,
  onAction,
}) => (
  <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30">
    <div className="h-12 w-12 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 mb-3">
      <Inbox className="w-6 h-6" />
    </div>
    <h4 className="text-base font-semibold text-slate-200">{title}</h4>
    <p className="text-xs text-slate-400 max-w-sm mt-1 mb-4">{description}</p>
    {actionText && onAction && (
      <button
        onClick={onAction}
        className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 transition"
      >
        {actionText}
      </button>
    )}
  </div>
);

interface ErrorStateProps {
  title?: string;
  error?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load telemetry',
  error = 'Could not establish connection with operations telemetry stream.',
  onRetry,
}) => (
  <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-rose-900/40 bg-rose-950/20">
    <div className="h-12 w-12 rounded-2xl bg-rose-900/40 border border-rose-800/60 flex items-center justify-center text-rose-400 mb-3">
      <AlertCircle className="w-6 h-6" />
    </div>
    <h4 className="text-base font-semibold text-rose-200">{title}</h4>
    <p className="text-xs text-rose-300/80 max-w-sm mt-1 mb-4">{error}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium transition"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Retry Connection</span>
      </button>
    )}
  </div>
);
