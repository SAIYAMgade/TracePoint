import React, { useEffect, useState } from 'react';
import {
  History,
  RotateCw,
  Search,
  Filter,
  ShieldCheck,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { AuditLogItem } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [entityFilter, setEntityFilter] = useState('');
  const [searchId, setSearchId] = useState('');

  const loadLogs = () => {
    setLoading(true);
    api.getAuditLogs({
      entity_type: entityFilter || undefined,
      entity_id: searchId || undefined,
      limit: 100
    })
      .then(setLogs)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLogs();
  }, [entityFilter, searchId]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <History className="h-5 w-5 text-indigo-400" />
            Immutable Audit History & Transaction Ledger
          </h2>
          <p className="text-xs text-slate-400">
            Cryptographically timestamped, append-only records of defect status transitions, test executions, and release gate evaluations.
          </p>
        </div>

        <button
          onClick={loadLogs}
          className="text-xs px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1.5 transition self-start sm:self-auto"
        >
          <RotateCw className="h-3.5 w-3.5" />
          Refresh Audit Trail
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-3 rounded-lg bg-[#0e1526] border border-slate-800 flex flex-wrap items-center gap-3 text-xs">
        <select
          value={entityFilter}
          onChange={(e) => setEntityFilter(e.target.value)}
          className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Entity Types</option>
          <option value="DEFECT">Defects</option>
          <option value="INVESTIGATION">Investigations</option>
          <option value="TEST_RUN">Test Runs</option>
          <option value="RELEASE">Releases</option>
          <option value="DATABASE_CHANGE">Database Changes</option>
          <option value="EVIDENCE">Evidence</option>
        </select>

        <input
          type="text"
          placeholder="Filter by Entity ID (e.g. DEF-101)..."
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs placeholder-slate-500 focus:outline-none focus:border-indigo-500 min-w-[200px]"
        />

        {(entityFilter || searchId) && (
          <button
            onClick={() => {
              setEntityFilter('');
              setSearchId('');
            }}
            className="text-xs text-slate-400 hover:text-slate-200 underline"
          >
            Reset Filters
          </button>
        )}
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl bg-[#0e1526] border border-slate-800/80 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[11px] font-mono text-slate-400 uppercase border-b border-slate-800 bg-slate-900/60">
              <tr>
                <th className="py-2.5 px-3">Audit ID</th>
                <th className="py-2.5 px-3">Entity Type</th>
                <th className="py-2.5 px-3">Entity ID</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">State Transition / Details</th>
                <th className="py-2.5 px-3">Actor</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    Loading audit trail from database...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    No audit records matching query.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.audit_id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-3 font-mono font-medium text-slate-400 text-[11px]">{log.audit_id}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                        {log.entity_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-indigo-400">{log.entity_id}</td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-200">{log.action}</td>
                    <td className="py-2.5 px-3 text-slate-300 max-w-sm truncate text-[11px]">
                      {log.previous_state && (
                        <span className="text-slate-500 font-mono mr-1.5">
                          {log.previous_state} →
                        </span>
                      )}
                      <span>{log.new_state}</span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{log.actor}</td>
                    <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px] whitespace-nowrap">
                      {log.created_at}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
