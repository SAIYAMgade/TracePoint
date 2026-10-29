import React, { useEffect, useState } from 'react';
import {
  Database,
  CheckCircle2,
  XCircle,
  Clock,
  Play,
  RotateCw,
  Terminal,
  FileCode2,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { DatabaseChange } from '../types';

export const DatabaseChangesPage: React.FC = () => {
  const [changes, setChanges] = useState<DatabaseChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChangeId, setSelectedChangeId] = useState<string>('CHG-001');
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  const loadChanges = () => {
    setLoading(true);
    api.getDatabaseChanges()
      .then((data) => {
        setChanges(data);
        if (data.length > 0 && !selectedChangeId) {
          setSelectedChangeId(data[0].change_id);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadChanges();
  }, []);

  const currentChange = changes.find((c) => c.change_id === selectedChangeId);

  const handleExecuteMigration = async () => {
    if (!currentChange) return;
    setExecuting(true);
    try {
      const res = await api.executeDatabaseChange(currentChange.change_id, 'alex.chen');
      setExecutionResult(res);
      loadChanges();
    } catch (err: any) {
      alert(`Migration failed: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <Database className="h-5 w-5 text-indigo-400" />
            Oracle Database Change Validation & Controlled Migrations
          </h2>
          <p className="text-xs text-slate-400">
            Pre-flight checks, deterministic DDL execution, post-migration object verification, and rollback safety.
          </p>
        </div>

        <button
          onClick={loadChanges}
          className="text-xs px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1.5 transition self-start sm:self-auto"
        >
          <RotateCw className="h-3.5 w-3.5" />
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Migration List */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-3">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
            Migration Catalog ({changes.length})
          </h3>

          <div className="space-y-2">
            {changes.map((c) => {
              const active = c.change_id === selectedChangeId;
              return (
                <div
                  key={c.change_id}
                  onClick={() => {
                    setSelectedChangeId(c.change_id);
                    setExecutionResult(null);
                  }}
                  className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                    active
                      ? 'bg-indigo-950/30 border-indigo-500/50 text-white'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-indigo-400">{c.change_id}</span>
                    <span
                      className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-bold ${
                        c.status === 'APPLIED'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <div className="font-medium truncate">{c.change_name}</div>
                  <div className="text-[11px] text-slate-500 font-mono mt-1">
                    Type: {c.change_type} | Schema: {c.target_schema}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Migration Inspector & Runner */}
        <div className="lg:col-span-2 space-y-4">
          {currentChange ? (
            <div className="p-5 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-semibold text-white">{currentChange.change_name}</h3>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Target Object: {currentChange.oracle_object_name || 'Schema Extension'}
                  </span>
                </div>

                <button
                  disabled={executing || currentChange.status === 'APPLIED'}
                  onClick={handleExecuteMigration}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-medium flex items-center gap-2 transition shadow-sm"
                >
                  {executing ? (
                    <>
                      <Activity className="h-3.5 w-3.5 animate-spin" />
                      Executing Pre/Up/Post Stages...
                    </>
                  ) : currentChange.status === 'APPLIED' ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Migration Already Applied
                    </>
                  ) : (
                    <>
                      <Play className="h-3.5 w-3.5 fill-current" />
                      Validate & Apply Controlled Migration
                    </>
                  )}
                </button>
              </div>

              {/* 3-Stage Migration Specification */}
              <div className="space-y-3 text-xs">
                {/* 1. Pre-Check */}
                <div>
                  <span className="font-mono text-[10px] text-amber-400 uppercase font-semibold block mb-1">
                    1. PRE-CHECK VALIDATION QUERY (Verifies precondition)
                  </span>
                  <pre className="p-2.5 rounded bg-black/60 text-slate-300 font-mono text-[11px] border border-slate-800 overflow-x-auto whitespace-pre-wrap">
                    {currentChange.pre_check_query || 'None specified'}
                  </pre>
                </div>

                {/* 2. Up Migration SQL */}
                <div>
                  <span className="font-mono text-[10px] text-indigo-400 uppercase font-semibold block mb-1">
                    2. UP MIGRATION DDL (Approved Controlled Script)
                  </span>
                  <pre className="p-2.5 rounded bg-black/60 text-slate-200 font-mono text-[11px] border border-slate-800 overflow-x-auto whitespace-pre-wrap">
                    {currentChange.sql_script}
                  </pre>
                </div>

                {/* 3. Post-Check */}
                <div>
                  <span className="font-mono text-[10px] text-emerald-400 uppercase font-semibold block mb-1">
                    3. POST-CHECK VERIFICATION QUERY (Confirms target object status)
                  </span>
                  <pre className="p-2.5 rounded bg-black/60 text-slate-300 font-mono text-[11px] border border-slate-800 overflow-x-auto whitespace-pre-wrap">
                    {currentChange.post_check_query || 'None specified'}
                  </pre>
                </div>

                {/* Rollback Script */}
                {currentChange.rollback_script && (
                  <div>
                    <span className="font-mono text-[10px] text-rose-400 uppercase font-semibold block mb-1">
                      ROLLBACK DDL & TRANSACTIONAL CONSIDERATIONS
                    </span>
                    <pre className="p-2 rounded bg-black/40 text-slate-400 font-mono text-[11px] border border-slate-800/80 overflow-x-auto whitespace-pre-wrap">
                      {currentChange.rollback_script}
                    </pre>
                    <p className="text-[10px] text-slate-500 mt-1 italic">
                      Note: In Oracle Database, DDL operations issue implicit commits. Rollback scripts must be executed explicitly.
                    </p>
                  </div>
                )}
              </div>

              {/* Execution Log Output */}
              {(currentChange.execution_log || executionResult) && (
                <div className="pt-3 border-t border-slate-800 space-y-1.5">
                  <span className="font-mono text-[10px] uppercase text-slate-400 font-semibold flex items-center gap-1.5">
                    <Terminal className="h-3.5 w-3.5 text-indigo-400" />
                    EXECUTION VERIFICATION LOG
                  </span>
                  <pre className="p-3 rounded-lg bg-black/90 text-emerald-300 font-mono text-[11px] leading-relaxed border border-slate-800 whitespace-pre-wrap">
                    {executionResult ? executionResult.execution_log : currentChange.execution_log}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 text-xs">Select a migration to inspect.</div>
          )}
        </div>
      </div>
    </div>
  );
};
