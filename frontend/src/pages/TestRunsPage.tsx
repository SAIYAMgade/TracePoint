import React, { useEffect, useState } from 'react';
import {
  PlaySquare,
  Terminal,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Play,
  RotateCw,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { TestRun } from '../types';

interface TestRunsPageProps {
  initialCommand?: string;
  initialDefectId?: string;
}

export const TestRunsPage: React.FC<TestRunsPageProps> = ({ initialCommand, initialDefectId }) => {
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);

  // Runner Console State
  const [selectedCommand, setSelectedCommand] = useState(
    initialCommand || 'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v'
  );
  const [defectId, setDefectId] = useState(initialDefectId || '');
  const [running, setRunning] = useState(false);
  const [latestOutput, setLatestOutput] = useState<TestRun | null>(null);

  const allowedCommands = [
    { cmd: 'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v', label: 'Scenario A: Date Boundary Suite' },
    { cmd: 'pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v', label: 'Scenario B: Duplicate Join Aggregate Suite' },
    { cmd: 'pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v', label: 'Scenario C: Workflow State Guard Suite' },
    { cmd: 'pytest demo_lab/tests/test_scenario_d_db_integrity.py -v', label: 'Scenario D: DB Constraint & Rollback Suite' },
    { cmd: 'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v', label: 'Scenario E: Discount Regression Suite' },
    { cmd: 'pytest demo_lab/tests/ -v', label: 'All Demonstration Lab Scenarios' },
    { cmd: 'pytest tests/unit/ -v', label: 'Core Unit Tests (State Machine & Release Gates)' },
    { cmd: 'pytest tests/api/ -v', label: 'API Endpoint Integration Tests' },
  ];

  const loadRuns = () => {
    setLoading(true);
    api.getTestRuns({ limit: 30 })
      .then((data) => {
        setRuns(data);
        if (data.length > 0 && !latestOutput) {
          setLatestOutput(data[0]);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadRuns();
  }, []);

  const handleRunCommand = async () => {
    setRunning(true);
    try {
      const res = await api.executeTest(
        selectedCommand,
        defectId || undefined,
        undefined,
        'developer'
      );
      setLatestOutput(res);
      loadRuns();
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <PlaySquare className="h-5 w-5 text-indigo-400" />
            Controlled Test Runner & Real-Time Terminal
          </h2>
          <p className="text-xs text-slate-400">
            Bounded execution of allowlisted test commands with real-time exit status, pass/fail metrics, and database logging.
          </p>
        </div>

        <button
          onClick={loadRuns}
          className="text-xs px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1.5 transition self-start sm:self-auto"
        >
          <RotateCw className="h-3.5 w-3.5" />
          Refresh Run Logs
        </button>
      </div>

      {/* Test Execution Console Panel */}
      <div className="p-5 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-4 shadow-sm">
        <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Terminal className="h-4 w-4 text-indigo-400" />
          ALLOWLISTED TEST EXECUTION CONSOLE
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2 space-y-1">
            <label className="text-[11px] font-mono text-slate-400">SELECT ALLOWLISTED TEST COMMAND</label>
            <select
              value={selectedCommand}
              onChange={(e) => setSelectedCommand(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:outline-none focus:border-indigo-500"
            >
              {allowedCommands.map((c) => (
                <option key={c.cmd} value={c.cmd}>
                  {c.cmd} ({c.label})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-mono text-slate-400">RELATED DEFECT ID (OPTIONAL)</label>
            <input
              type="text"
              placeholder="e.g. DEF-101"
              value={defectId}
              onChange={(e) => setDefectId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <span className="text-[11px] text-slate-400 font-mono">
            Security: Unrestricted shell execution is forbidden. Only allowlisted pytest targets run.
          </span>
          <button
            disabled={running}
            onClick={handleRunCommand}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-2 transition disabled:opacity-50 shadow-sm"
          >
            {running ? (
              <>
                <Activity className="h-4 w-4 animate-spin" />
                Executing in isolated process...
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                Execute Command
              </>
            )}
          </button>
        </div>

        {/* Live Terminal Output Console */}
        {latestOutput && (
          <div className="mt-3 rounded-lg bg-black/90 border border-slate-800 p-4 font-mono text-xs text-slate-200 space-y-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 text-[11px]">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">RUN ID:</span>
                <span className="text-indigo-400 font-bold">{latestOutput.run_id}</span>
                <span className="text-slate-500">|</span>
                <span className="text-slate-400">COMMAND:</span>
                <span className="text-slate-300">{latestOutput.command}</span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    latestOutput.outcome === 'PASSED'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}
                >
                  {latestOutput.outcome}
                </span>
                <span className="text-slate-400">{latestOutput.duration_ms}ms</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 py-1 text-[11px] text-slate-400">
              <div>
                Passed: <span className="text-emerald-400 font-bold">{latestOutput.passed_count}</span>
              </div>
              <div>
                Failed: <span className="text-rose-400 font-bold">{latestOutput.failed_count}</span>
              </div>
              <div>
                Skipped: <span className="text-slate-400 font-bold">{latestOutput.skipped_count}</span>
              </div>
            </div>

            <pre className="p-3 rounded bg-[#070a12] text-slate-300 text-[11px] overflow-x-auto whitespace-pre-wrap max-h-56 leading-relaxed border border-slate-800/80">
              {latestOutput.output_summary}
            </pre>
          </div>
        )}
      </div>

      {/* Historical Test Runs Table */}
      <div className="rounded-xl bg-[#0e1526] border border-slate-800/80 overflow-hidden">
        <div className="p-3.5 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
            Historical Test Execution Log ({runs.length})
          </h3>
          <span className="text-[11px] text-slate-400">Audit-backed execution history</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[11px] font-mono text-slate-400 uppercase border-b border-slate-800 bg-slate-900/40">
              <tr>
                <th className="py-2.5 px-3">Run ID</th>
                <th className="py-2.5 px-3">Outcome</th>
                <th className="py-2.5 px-3">Command / Suite</th>
                <th className="py-2.5 px-3">Passed</th>
                <th className="py-2.5 px-3">Failed</th>
                <th className="py-2.5 px-3">Duration</th>
                <th className="py-2.5 px-3">Guards Defect</th>
                <th className="py-2.5 px-3">Completed At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {runs.map((r) => (
                <tr
                  key={r.run_id}
                  onClick={() => setLatestOutput(r)}
                  className="hover:bg-slate-800/40 cursor-pointer transition"
                >
                  <td className="py-2.5 px-3 font-mono font-medium text-indigo-400">{r.run_id}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        r.outcome === 'PASSED'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/40'
                          : 'bg-rose-950 text-rose-300 border border-rose-800/40'
                      }`}
                    >
                      {r.outcome}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-300 max-w-xs truncate">
                    {r.command}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-emerald-400">{r.passed_count}</td>
                  <td className="py-2.5 px-3 font-mono text-rose-400">{r.failed_count}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">{r.duration_ms}ms</td>
                  <td className="py-2.5 px-3 font-mono text-indigo-300">{r.related_defect_id || '—'}</td>
                  <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{r.completed_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
