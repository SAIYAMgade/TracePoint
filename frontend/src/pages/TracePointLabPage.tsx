import React, { useState } from 'react';
import {
  FlaskConical,
  Play,
  RotateCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Code2,
  Terminal,
  Activity
} from 'lucide-react';
import { api } from '../api/client';

interface TracePointLabPageProps {
  onNavigateToTest: (command: string) => void;
}

export const TracePointLabPage: React.FC<TracePointLabPageProps> = ({ onNavigateToTest }) => {
  const [activeScenario, setActiveScenario] = useState<'A' | 'B' | 'C' | 'D' | 'E'>('A');
  const [mode, setMode] = useState<'buggy' | 'fixed'>('buggy');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Scenario specific params
  const [scenarioCApproved, setScenarioCApproved] = useState(false);
  const [scenarioCAmount, setScenarioCAmount] = useState(75000);

  const runScenario = async () => {
    setLoading(true);
    setResult(null);
    try {
      let res;
      if (activeScenario === 'A') {
        res = await api.runScenarioA('2026-09-01', '2026-09-30', mode);
      } else if (activeScenario === 'B') {
        res = await api.runScenarioB('ORD-99', mode);
      } else if (activeScenario === 'C') {
        res = await api.runScenarioC('DRAFT', 'ISSUED', scenarioCAmount, scenarioCApproved, mode);
      } else if (activeScenario === 'D') {
        res = await api.runScenarioD(mode);
      } else if (activeScenario === 'E') {
        res = await api.runScenarioE(100.0, 'SUMMER20', '2026-06-01', mode);
      }
      setResult(res);
    } catch (err: any) {
      alert(`Scenario execution error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const scenarios = [
    {
      id: 'A',
      title: 'Scenario A: Incorrect Date Boundary',
      defectId: 'DEF-101',
      testCmd: 'pytest demo_lab/tests/test_scenario_a_date_boundary.py -v',
      desc: 'Reporting query omits transaction records occurring on the midnight date boundary (e.g. 23:59:59.000).'
    },
    {
      id: 'B',
      title: 'Scenario B: Duplicate Join Aggregate Results',
      defectId: 'DEF-102',
      testCmd: 'pytest demo_lab/tests/test_scenario_b_duplicate_aggregation.py -v',
      desc: 'Missing line-item grouping in orders-to-shipments join causes cartesian fan-out, inflating sales 3x-5x.'
    },
    {
      id: 'C',
      title: 'Scenario C: Invalid Workflow Transition',
      defectId: 'DEF-103',
      testCmd: 'pytest demo_lab/tests/test_scenario_c_invalid_transition.py -v',
      desc: 'High-value enterprise invoices bypass mandatory credit approval and transition directly from DRAFT to ISSUED.'
    },
    {
      id: 'D',
      title: 'Scenario D: DB Constraint & Rollback Failure',
      defectId: 'DEF-104',
      testCmd: 'pytest demo_lab/tests/test_scenario_d_db_integrity.py -v',
      desc: 'Batch processing without explicit transaction boundary leaves orphaned rows on ORA-02291 integrity failure.'
    },
    {
      id: 'E',
      title: 'Scenario E: Regression After Optimization',
      defectId: 'DEF-105',
      testCmd: 'pytest demo_lab/tests/test_scenario_e_regression_guard.py -v',
      desc: 'Performance optimization accidentally bypasses coupon expiration checks, accepting expired discount codes.'
    },
  ];

  const current = scenarios.find((s) => s.id === activeScenario)!;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-gradient-to-r from-purple-950/40 via-slate-900 to-indigo-950/40 border border-purple-800/40">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-purple-400" />
            TracePoint Lab: Controlled Synthetic Scenarios
          </h2>
          <p className="text-xs text-slate-400">
            Isolated demonstration environment executing deterministic fixtures, reproducible failures, and verified regression guards.
          </p>
        </div>

        <div className="text-xs font-mono text-purple-300 bg-purple-950/60 px-3 py-1.5 rounded border border-purple-700/50">
          DEMONSTRATION RUNNER
        </div>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
        {scenarios.map((s) => {
          const active = s.id === activeScenario;
          return (
            <button
              key={s.id}
              onClick={() => {
                setActiveScenario(s.id as any);
                setResult(null);
              }}
              className={`p-3 rounded-lg border text-left text-xs transition flex flex-col justify-between ${
                active
                  ? 'bg-purple-950/40 border-purple-500/60 text-white shadow-sm'
                  : 'bg-[#0e1526] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <span className="font-mono font-bold text-purple-400 block mb-1">{s.defectId}</span>
              <span className="font-medium text-slate-200 line-clamp-1">{s.title}</span>
            </button>
          );
        })}
      </div>

      {/* Scenario Interactive Card */}
      <div className="p-6 rounded-xl bg-[#0e1526] border border-slate-800 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold text-white">{current.title}</span>
              <span className="px-2 py-0.5 rounded font-mono text-[10px] bg-slate-800 text-indigo-300 border border-slate-700">
                Guards {current.defectId}
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">{current.desc}</p>
          </div>

          {/* Mode Switcher Toggle */}
          <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800 self-start md:self-auto">
            <button
              onClick={() => setMode('buggy')}
              className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition ${
                mode === 'buggy'
                  ? 'bg-rose-950 text-rose-300 border border-rose-800'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              1. Buggy Implementation
            </button>
            <button
              onClick={() => setMode('fixed')}
              className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition ${
                mode === 'fixed'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              2. Corrected & Verified
            </button>
          </div>
        </div>

        {/* Dynamic Controls for Scenario C */}
        {activeScenario === 'C' && (
          <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">Invoice Amount ($)</label>
              <input
                type="number"
                value={scenarioCAmount}
                onChange={(e) => setScenarioCAmount(Number(e.target.value))}
                className="w-full px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-200 font-mono text-xs"
              />
            </div>
            <div className="flex items-center gap-2 pt-4">
              <input
                type="checkbox"
                id="credit_appr"
                checked={scenarioCApproved}
                onChange={(e) => setScenarioCApproved(e.target.checked)}
                className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
              />
              <label htmlFor="credit_appr" className="text-slate-300 cursor-pointer">
                Credit Pre-approval Granted
              </label>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <button
            disabled={loading}
            onClick={runScenario}
            className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium flex items-center gap-2 transition disabled:opacity-50 shadow-sm"
          >
            {loading ? (
              <>
                <Activity className="h-4 w-4 animate-spin" />
                Executing synthetic fixture...
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                Execute in {mode === 'buggy' ? 'Buggy Mode' : 'Corrected Mode'}
              </>
            )}
          </button>

          <button
            onClick={() => onNavigateToTest(current.testCmd)}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1.5 underline"
          >
            <span>Run Automated Regression Suite in Test Runner</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Result Output Display */}
        {result && (
          <div className="mt-4 rounded-xl bg-slate-950 border border-slate-800 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-white">Execution Result:</span>
                <span className="font-mono text-xs text-slate-400">Mode: {result.mode}</span>
              </div>

              {result.defect_observed ? (
                <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800 flex items-center gap-1">
                  <XCircle className="h-3.5 w-3.5" /> DEFECT REPRODUCED
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5" /> VERIFIED BEHAVIOR
                </span>
              )}
            </div>

            {/* Explanation Callout */}
            <div
              className={`p-3 rounded-lg text-xs leading-relaxed ${
                result.defect_observed
                  ? 'bg-rose-950/30 border border-rose-900/50 text-rose-200'
                  : 'bg-emerald-950/30 border border-emerald-900/50 text-emerald-200'
              }`}
            >
              <span className="font-semibold block mb-0.5">Engineering Observation:</span>
              {result.explanation || result.message}
            </div>

            {/* Formatted JSON Payload */}
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                Deterministic Output Payload
              </span>
              <pre className="p-3 rounded-lg bg-black/80 text-indigo-300 font-mono text-[11px] overflow-x-auto border border-slate-800">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
