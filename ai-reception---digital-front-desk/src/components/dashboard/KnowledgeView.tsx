import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Upload,
  Search,
  CheckCircle2,
  FileText,
  Clock,
  Building,
  Sparkles,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { LoadingState, EmptyState, ErrorState } from './StateViews';
import { KnowledgeDocument } from '../../types/dashboard';

export const KnowledgeView: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // RAG Search Tester State
  const [testQuery, setTestQuery] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  // Upload simulation state
  const [isUploading, setIsUploading] = useState(false);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      setError(null);
      const items = await DashboardService.getKnowledgeDocuments();
      setDocuments(items);
    } catch (err: any) {
      setError(err?.message || 'Failed to load knowledge corpus');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleTestSearch = async () => {
    if (!testQuery.trim()) return;
    setTesting(true);
    try {
      const res = await DashboardService.testKnowledgeSearch(testQuery);
      setTestResult(res);
    } catch {
      setTestResult(null);
    } finally {
      setTesting(false);
    }
  };

  const handleSimulateUpload = async () => {
    setIsUploading(true);
    await DashboardService.uploadDocument(
      'TCMIT Code of Conduct & Student Handbook 2026.pdf',
      '3.2 MB',
      'Student Affairs'
    );
    await fetchDocs();
    setIsUploading(false);
  };

  return (
    <div className="space-y-6 select-none pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Institutional Knowledge Base (RAG)</h2>
          <p className="text-xs text-slate-400">
            Authoritative documents grounding the AI Receptionist against hallucinations
          </p>
        </div>

        <button
          onClick={handleSimulateUpload}
          disabled={isUploading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 transition disabled:opacity-50"
        >
          <Upload className="w-4 h-4" />
          <span>{isUploading ? 'Indexing PDF...' : 'Upload New Document'}</span>
        </button>
      </div>

      {/* Interactive RAG Testing Sandbox */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-950 border border-blue-500/40 shadow-xl space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white">RAG Grounding Verification Sandbox</h3>
        </div>
        <p className="text-xs text-slate-300">
          Simulate how the reception AI vectorizes and retrieves verified passages for visitor questions.
        </p>

        <div className="flex flex-col sm:flex-row gap-2 pt-1">
          <input
            type="text"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleTestSearch()}
            placeholder="e.g. 'What are the BIT qualification requirements?' or 'How to meet Principal?'"
            className="flex-1 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
          />
          <button
            onClick={handleTestSearch}
            disabled={testing || !testQuery.trim()}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition disabled:opacity-50 flex items-center justify-center gap-1.5"
          >
            <Search className="w-3.5 h-3.5" />
            <span>{testing ? 'Testing...' : 'Test Retrieval'}</span>
          </button>
        </div>

        {/* Test Result Display */}
        {testResult && (
          <div
            className={`p-3.5 rounded-xl border text-xs mt-2 ${
              testResult.matched
                ? 'bg-blue-950/40 border-blue-800/60'
                : 'bg-amber-950/30 border-amber-800/50'
            }`}
          >
            <div className="flex items-center justify-between font-mono-code text-[11px] mb-1">
              <span className={testResult.matched ? 'text-cyan-400 font-bold' : 'text-amber-400'}>
                {testResult.matched ? 'RETRIEVED PASSAGE (VERIFIED)' : 'CONFIDENCE BELOW THRESHOLD'}
              </span>
              <span className="text-slate-400">Score: {(testResult.score * 100).toFixed(1)}%</span>
            </div>

            <p className="text-slate-200 italic bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80 my-1">
              "{testResult.retrievedParagraph}"
            </p>

            {testResult.source && (
              <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-1">
                <span>Source: <strong className="text-slate-200">{testResult.source.document}</strong></span>
                <span>·</span>
                <span>Page {testResult.source.page}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Uploaded Documents List */}
      {loading ? (
        <LoadingState message="Reading indexed documents from knowledge store..." />
      ) : error ? (
        <ErrorState title="Knowledge Error" error={error} onRetry={fetchDocs} />
      ) : documents.length === 0 ? (
        <EmptyState title="No documents uploaded" description="Upload a PDF policy or curriculum to ground the AI." />
      ) : (
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/60">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-code">
              Active Grounding Documents ({documents.length})
            </h3>
          </div>
          <div className="divide-y divide-slate-800/60">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/40 transition"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2.5 rounded-xl bg-blue-950 border border-blue-800 text-blue-400 shrink-0 mt-0.5">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{doc.name}</h4>
                    <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 mt-1">
                      <span>Size: {doc.size}</span>
                      <span>·</span>
                      <span>Pages: {doc.pages}</span>
                      <span>·</span>
                      <span>Dept: {doc.department}</span>
                      <span>·</span>
                      <span>Indexed: {doc.lastIndexed}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <span className="flex items-center gap-1 text-[10px] font-mono-code px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    <span>{doc.status}</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
