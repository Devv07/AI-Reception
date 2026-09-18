import React, { useState, useEffect } from 'react';
import {
  Settings,
  Building,
  Bot,
  Shield,
  Save,
  CheckCircle2,
  Lock,
  Volume2,
  Camera,
} from 'lucide-react';
import { DashboardService } from '../../services/dashboardService';
import { LoadingState, ErrorState } from './StateViews';
import { OrganizationSettings } from '../../types/dashboard';

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<OrganizationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await DashboardService.getSettings();
      setSettings(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load organization settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;
    setSaving(true);
    try {
      await DashboardService.updateSettings(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch {
      // Error
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState message="Fetching system configurations..." />;
  if (error || !settings) return <ErrorState title="Settings Error" error={error || 'No data'} onRetry={fetchSettings} />;

  return (
    <form onSubmit={handleSave} className="space-y-6 select-none pb-8 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">AI Reception & Organization Settings</h2>
          <p className="text-xs text-slate-400">
            Configure institutional parameters, bilingual greetings, and hardware privacy
          </p>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-2 px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 transition disabled:opacity-50"
        >
          {saveSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              <span>Saved Successfully</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
            </>
          )}
        </button>
      </div>

      {/* Section 1: Institutional Profile */}
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <Building className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-code">
            Organization Profile
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Institution Legal Name</label>
            <input
              type="text"
              value={settings.name}
              onChange={(e) => setSettings({ ...settings, name: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Campus Code</label>
            <input
              type="text"
              value={settings.code}
              onChange={(e) => setSettings({ ...settings, code: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition font-mono-code"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-slate-400 mb-1">Physical Campus Address</label>
            <input
              type="text"
              value={settings.address}
              onChange={(e) => setSettings({ ...settings, address: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Contact Phone</label>
            <input
              type="text"
              value={settings.contactPhone}
              onChange={(e) => setSettings({ ...settings, contactPhone: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition font-mono-code"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Reception Email</label>
            <input
              type="email"
              value={settings.contactEmail}
              onChange={(e) => setSettings({ ...settings, contactEmail: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
        </div>
      </div>

      {/* Section 2: Reception AI Greetings & Unknown Handling */}
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <Bot className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-code">
            Reception AI Greetings & Boundary Behaviors
          </h3>
        </div>

        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">English Welcome Prompt</label>
            <input
              type="text"
              value={settings.greetingEn}
              onChange={(e) => setSettings({ ...settings, greetingEn: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Nepali Welcome Prompt (Devanagari)</label>
            <input
              type="text"
              value={settings.greetingNe}
              onChange={(e) => setSettings({ ...settings, greetingNe: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">
              Responsible AI Unknown Question Response (Zero Hallucination)
            </label>
            <textarea
              rows={2}
              value={settings.fallbackResponse}
              onChange={(e) => setSettings({ ...settings, fallbackResponse: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Default Human Escalation Desk</label>
            <input
              type="text"
              value={settings.handoffDutyDesk}
              onChange={(e) => setSettings({ ...settings, handoffDutyDesk: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500 transition"
            />
          </div>
        </div>
      </div>

      {/* Section 3: Hardware & Sensor Privacy */}
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <Shield className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-code">
            Hardware & Biometric Privacy Safeguards
          </h3>
        </div>

        <div className="space-y-3 text-xs">
          <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
            <div>
              <span className="font-semibold text-slate-200 block">Presence Detection Sensor</span>
              <span className="text-[11px] text-slate-400">
                Wakes reception screen when visitor approaches within 1.5 meters
              </span>
            </div>
            <input
              type="checkbox"
              checked={settings.cameraDetectionEnabled}
              onChange={(e) =>
                setSettings({ ...settings, cameraDetectionEnabled: e.target.checked })
              }
              className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0 cursor-pointer"
            />
          </label>

          <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
            <div>
              <span className="font-semibold text-slate-200 block">Strict Ephemeral Privacy Mode</span>
              <span className="text-[11px] text-slate-400">
                Guaranteed: No facial images, biometrics, or audio recordings persisted to disk
              </span>
            </div>
            <input
              type="checkbox"
              checked={settings.privacyMode}
              onChange={(e) => setSettings({ ...settings, privacyMode: e.target.checked })}
              className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0 cursor-pointer"
            />
          </label>
        </div>
      </div>
    </form>
  );
};
