import React, { useEffect, useState } from 'react';
import {
  FileCheck2,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Terminal,
  ArrowRight,
  ShieldAlert,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { RegressionTest, TestRun } from '../types';

interface RegressionTestsPageProps {
  onRunTest: (command: string, defectId?: string) => void;
}

export const RegressionTestsPage: React.FC<RegressionTestsPageProps> = ({ onRunTest }) => {
  const [tests, setTests] = useState<RegressionTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingTestId, setExecutingTestId] = useState<string | null>(null);

  const loadTests = () => {
    setLoading(true);
    api.getRegressionTests()
      .then(setTests)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTests();
  }, []);

  const handleQuickExecute = async (test: RegressionTest) => {
    setExecutingTestId(test.test_id);
    try {
      await api.executeTest(test.execution_command, test.related_defect_id);
      loadTests();
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setExecutingTestId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <FileCheck2 className="h-5 w-5 text-indigo-400" />
            Automated Regression Test Catalog
          </h2>
          <p className="text-xs text-slate-400">
            Automated tests preventing defect recurrence across date boundaries, SQL aggregations, state guards, and transactions.
          </p>
        </div>

        <button
          onClick={() => onRunTest('pytest demo_lab/tests/ -v')}
          className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 transition shadow-sm self-start sm:self-auto"
        >
          <Play className="h-3.5 w-3.5" />
          Run All Regression Suites
        </button>
      </div>

      {/* Tests Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 text-center py-8 text-slate-400 text-xs">
            Loading regression catalog...
          </div>
        ) : (
          tests.map((test) => (
            <div
              key={test.test_id}
              className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 hover:border-slate-700/80 transition flex flex-col justify-between space-y-3"
            >
              <div>
                {/* Header row */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-indigo-400">{test.test_id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                      {test.test_category}
                    </span>
                  </div>

                  {/* Outcome badge */}
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1 ${
                      test.last_outcome === 'PASSED'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : test.last_outcome === 'FAILED'
                        ? 'bg-rose-950 text-rose-300 border border-rose-800'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {test.last_outcome === 'PASSED' && <CheckCircle2 className="h-3 w-3" />}
                    {test.last_outcome === 'FAILED' && <XCircle className="h-3 w-3" />}
                    {test.last_outcome}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-white leading-snug">{test.title}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{test.description}</p>
              </div>

              {/* Behavior & Preconditions */}
              <div className="p-2.5 rounded bg-slate-900/80 border border-slate-800/80 text-xs space-y-1">
                <div className="text-[11px] text-slate-300">
                  <span className="font-mono text-[10px] uppercase text-slate-500 mr-1.5">Expected:</span>
                  {test.expected_behavior}
                </div>
                {test.related_defect_id && (
                  <div className="text-[11px] text-slate-400 font-mono">
                    <span className="text-[10px] uppercase text-slate-500 mr-1.5">Guards Defect:</span>
                    <span className="text-indigo-400">{test.related_defect_id}</span>
                  </div>
                )}
              </div>

              {/* Command & Execution Action */}
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                <div className="font-mono text-[11px] text-slate-500 truncate max-w-[240px]">
                  {test.execution_command}
                </div>

                <button
                  disabled={executingTestId === test.test_id}
                  onClick={() => handleQuickExecute(test)}
                  className="px-3 py-1 rounded bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-medium hover:bg-indigo-600/30 transition flex items-center gap-1 disabled:opacity-50"
                >
                  {executingTestId === test.test_id ? (
                    <>
                      <Activity className="h-3.5 w-3.5 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3" />
                      Run Test
                    </>
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
