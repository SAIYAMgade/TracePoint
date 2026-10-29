import React, { useEffect, useState } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Server,
  Database,
  Cpu,
  ShieldCheck,
  RotateCw
} from 'lucide-react';
import { api } from '../api/client';
import { SystemHealth } from '../types';

export const HealthPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const loadHealth = () => {
    setLoading(true);
    api.getHealth()
      .then(setHealth)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadHealth();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400 text-xs">
        <Activity className="h-4 w-4 animate-spin mr-2 text-indigo-400" />
        Checking system services and database connectivity...
      </div>
    );
  }

  const isOracle = health?.database?.is_oracle ?? false;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-400" />
            System Health, Database Dialect & Diagnostics
          </h2>
          <p className="text-xs text-slate-400">
            Runtime database engine capabilities, driver status, and test isolation environment.
          </p>
        </div>

        <button
          onClick={loadHealth}
          className="text-xs px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1.5 transition self-start sm:self-auto"
        >
          <RotateCw className="h-3.5 w-3.5" />
          Re-test Health
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database Health Card */}
        <div className="p-5 rounded-xl bg-[#0e1526] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Database className="h-4 w-4 text-indigo-400" />
              RELATIONAL DATABASE LAYER
            </h3>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1 ${
                health?.database?.connection_status === 'ONLINE'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  : 'bg-rose-950 text-rose-300 border border-rose-800'
              }`}
            >
              <CheckCircle2 className="h-3 w-3" />
              {health?.database?.connection_status}
            </span>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Active Dialect Engine:</span>
              <span className="font-mono font-bold text-slate-200 uppercase">
                {health?.database?.active_dialect}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Database Server Version:</span>
              <span className="font-mono text-indigo-300">
                {health?.database?.server_version}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Python Oracle Driver:</span>
              <span className="font-mono text-emerald-400">
                {health?.database?.driver_available ? 'python-oracledb 26.1.0 (Installed)' : 'Missing'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Total Defect Records:</span>
              <span className="font-mono font-bold text-white">
                {health?.database?.defect_records_count ?? 0}
              </span>
            </div>
          </div>

          {health?.database?.fallback_notice && (
            <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 text-amber-300 text-xs">
              <span className="font-semibold block mb-0.5">Database Engine Notice:</span>
              {health.database.fallback_notice}
            </div>
          )}

          <div>
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-2">
              Verified Capabilities in Active Environment
            </span>
            <div className="space-y-1">
              {health?.database?.verified_oracle_capabilities?.map((cap, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                  <span>{cap}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Runtime Environment Card */}
        <div className="p-5 rounded-xl bg-[#0e1526] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Server className="h-4 w-4 text-purple-400" />
              BACKEND RUNTIME & PROCESS ISOLATION
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-800">
              ACTIVE
            </span>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Service:</span>
              <span className="font-mono font-bold text-slate-200">{health?.service}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Environment:</span>
              <span className="font-mono text-slate-300 uppercase">{health?.environment}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">TracePoint Lab Service:</span>
              <span className="font-mono text-emerald-400">Operational (Scenarios A - E)</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Test Execution Security:</span>
              <span className="font-mono text-indigo-300">Allowlisted Subprocess Runner</span>
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-2">
            <span className="font-semibold text-slate-200 block">Interview Demonstration Sequence:</span>
            <ol className="list-decimal list-inside space-y-1 text-slate-400 text-[11px] leading-relaxed">
              <li><strong className="text-slate-300">Minute 1:</strong> Reproduce defect in Defect Registry / TracePoint Lab.</li>
              <li><strong className="text-slate-300">Minute 2:</strong> Review technical evidence in Investigation Workspace.</li>
              <li><strong className="text-slate-300">Minute 3:</strong> Execute regression test in Controlled Test Runner.</li>
              <li><strong className="text-slate-300">Minute 4:</strong> Validate DB change & constraint rollback in DB Validation.</li>
              <li><strong className="text-slate-300">Minute 5:</strong> Evaluate release readiness against objective checks.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};
