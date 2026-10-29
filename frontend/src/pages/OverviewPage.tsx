import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  Clock,
  CheckCircle2,
  XCircle,
  FileSearch,
  ShieldX,
  RotateCcw,
  Timer,
  ArrowRight,
  TrendingUp,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { DashboardMetrics, Defect } from '../types';

interface OverviewPageProps {
  onNavigate: (tab: string, filter?: { status?: string; severity?: string }) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentDefects, setRecentDefects] = useState<Defect[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getDashboardMetrics(), api.getDefects({ limit: 5 })])
      .then(([m, d]) => {
        setMetrics(m);
        setRecentDefects(d.items);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-xs">
        <Activity className="h-4 w-4 animate-spin mr-2 text-indigo-400" />
        Calculating engineering metrics from persisted database records...
      </div>
    );
  }

  const sev = metrics?.open_defects_by_severity || { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight">Engineering Reliability Overview</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time quality intelligence linking defects, technical evidence, regression test outcomes, and release gates.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('lab')}
            className="px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-medium hover:bg-indigo-600/30 transition flex items-center gap-1.5"
          >
            <span>Reproduce Synthetic Scenarios</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Open Defects by Severity */}
        <div
          onClick={() => onNavigate('defects')}
          className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 hover:border-slate-700 transition cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>OPEN DEFECTS BY SEVERITY</span>
            <AlertCircle className="h-4 w-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2 mb-3">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics?.total_active_defects ?? 0}
            </span>
            <span className="text-[11px] text-slate-500">unresolved</span>
          </div>
          <div className="grid grid-cols-4 gap-1 text-center font-mono text-[10px]">
            <div className="p-1 rounded bg-rose-950/50 text-rose-300 border border-rose-800/40">
              <span className="block font-bold">{sev.CRITICAL}</span>
              <span className="text-[9px] text-rose-400">CRIT</span>
            </div>
            <div className="p-1 rounded bg-amber-950/50 text-amber-300 border border-amber-800/40">
              <span className="block font-bold">{sev.HIGH}</span>
              <span className="text-[9px] text-amber-400">HIGH</span>
            </div>
            <div className="p-1 rounded bg-blue-950/50 text-blue-300 border border-blue-800/40">
              <span className="block font-bold">{sev.MEDIUM}</span>
              <span className="text-[9px] text-blue-400">MED</span>
            </div>
            <div className="p-1 rounded bg-slate-800/50 text-slate-300 border border-slate-700/40">
              <span className="block font-bold">{sev.LOW}</span>
              <span className="text-[9px] text-slate-400">LOW</span>
            </div>
          </div>
        </div>

        {/* Defects Awaiting Reproduction */}
        <div
          onClick={() => onNavigate('defects', { status: 'OPEN' })}
          className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 hover:border-slate-700 transition cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>AWAITING REPRODUCTION</span>
            <Clock className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics?.defects_awaiting_reproduction ?? 0}
            </span>
            <span className="text-[11px] text-amber-400 font-medium">pending verification</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Defects requiring deterministic reproduction steps and synthetic fixture validation.
          </p>
        </div>

        {/* Unconfirmed Investigations */}
        <div
          onClick={() => onNavigate('investigations')}
          className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 hover:border-slate-700 transition cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>UNCONFIRMED ROOT CAUSES</span>
            <FileSearch className="h-4 w-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics?.investigations_without_root_cause ?? 0}
            </span>
            <span className="text-[11px] text-purple-400 font-medium">hypotheses only</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Active investigations where hypothesis has not yet been established with technical evidence.
          </p>
        </div>

        {/* Blocked Releases */}
        <div
          onClick={() => onNavigate('releases')}
          className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 hover:border-slate-700 transition cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>BLOCKED RELEASES</span>
            <ShieldX className="h-4 w-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics?.releases_blocked ?? 0}
            </span>
            <span className="text-[11px] text-rose-400 font-medium">gates tripped</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Releases blocked by outstanding checks, open critical bugs, or failed regression runs.
          </p>
        </div>
      </div>

      {/* Secondary Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />
            <span>Fixes Awaiting Verification</span>
          </div>
          <span className="text-lg font-bold font-mono text-white">{metrics?.fixes_awaiting_verification ?? 0}</span>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <XCircle className="h-3.5 w-3.5 text-rose-400" />
            <span>Failed Regression Tests</span>
          </div>
          <span className="text-lg font-bold font-mono text-white">{metrics?.failed_regression_tests ?? 0}</span>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <RotateCcw className="h-3.5 w-3.5 text-amber-400" />
            <span>Reopened Defects</span>
          </div>
          <span className="text-lg font-bold font-mono text-white">{metrics?.reopened_defects_count ?? 0}</span>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Timer className="h-3.5 w-3.5 text-emerald-400" />
            <span>Avg Resolution Time</span>
          </div>
          <span className="text-lg font-bold font-mono text-white">
            {metrics?.avg_resolution_hours ? `${metrics.avg_resolution_hours} hrs` : 'N/A (< 2 resolved)'}
          </span>
        </div>
      </div>

      {/* Recent Investigations & Blocker Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Defect Triage Table */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#0e1526] border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Recent Defect Investigations</h3>
              <p className="text-xs text-slate-400">Direct link to reproduction workspace, hypotheses, and tests</p>
            </div>
            <button
              onClick={() => onNavigate('defects')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              View all ({metrics?.total_active_defects ?? 0})
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] font-mono text-slate-400 uppercase border-b border-slate-800 bg-slate-900/50">
                <tr>
                  <th className="py-2.5 px-3">Defect ID</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Summary</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Owner</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentDefects.map((d) => (
                  <tr
                    key={d.defect_id}
                    onClick={() => onNavigate('investigations')}
                    className="hover:bg-slate-800/40 cursor-pointer transition"
                  >
                    <td className="py-2.5 px-3 font-mono font-medium text-indigo-400">{d.defect_id}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                          d.severity === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800/50'
                            : d.severity === 'HIGH'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800/50'
                            : 'bg-blue-950 text-blue-300 border border-blue-800/50'
                        }`}
                      >
                        {d.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-300 font-medium max-w-xs truncate">{d.title}</td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">{d.status}</td>
                    <td className="py-2.5 px-3 text-slate-400">{d.assigned_owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Release Gate Blockers Panel */}
        <div className="p-5 rounded-xl bg-[#0e1526] border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white">Release Gate Status</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                BLOCKED
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Target Release <span className="text-white font-mono font-semibold">REL-2026.1.0</span> cannot proceed to deployment until all mandatory checks satisfy objective criteria.
            </p>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded bg-rose-950/20 border border-rose-900/40 flex items-start gap-2">
                <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-rose-200">Mandatory Regression Suite Failed</span>
                  <p className="text-[11px] text-rose-300/80">test_scenario_e_regression_guard failed on expired coupon calculation.</p>
                </div>
              </div>

              <div className="p-2.5 rounded bg-amber-950/20 border border-amber-900/40 flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-amber-200">4 Open Critical/High Defects</span>
                  <p className="text-[11px] text-amber-300/80">DEF-101, DEF-102, DEF-104, DEF-105 require verification.</p>
                </div>
              </div>

              <div className="p-2.5 rounded bg-slate-900/70 border border-slate-800 flex items-start gap-2">
                <Clock className="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-slate-300">Security Smoke Suite Pending</span>
                  <p className="text-[11px] text-slate-400">Awaiting execution in staging environment.</p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => onNavigate('releases')}
            className="w-full mt-5 py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition text-center"
          >
            Inspect Release Readiness Engine
          </button>
        </div>
      </div>
    </div>
  );
};
