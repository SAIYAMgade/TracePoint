import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  RotateCw,
  AlertTriangle,
  Play,
  FileText,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { Release, ReleaseCheck } from '../types';

export const ReleaseReadinessPage: React.FC = () => {
  const [releases, setReleases] = useState<Release[]>([]);
  const [selectedReleaseId, setSelectedReleaseId] = useState<string>('REL-2026.1.0');
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<any>(null);

  // Check editing state
  const [editingCheck, setEditingCheck] = useState<ReleaseCheck | null>(null);
  const [editStatus, setEditStatus] = useState<ReleaseCheck['status']>('PASSED');
  const [waiverReason, setWaiverReason] = useState('');
  const [evidenceDetails, setEvidenceDetails] = useState('');

  const loadReleases = () => {
    setLoading(true);
    api.getReleases()
      .then((data) => {
        setReleases(data);
        if (data.length > 0 && !selectedReleaseId) {
          setSelectedReleaseId(data[0].release_id);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadReleases();
  }, []);

  const currentRelease = releases.find((r) => r.release_id === selectedReleaseId);

  const handleEvaluate = async () => {
    if (!currentRelease) return;
    setEvaluating(true);
    try {
      const res = await api.evaluateRelease(currentRelease.release_id);
      setEvaluationResult(res);
      loadReleases();
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  const handleSaveCheck = async () => {
    if (!editingCheck || !currentRelease) return;
    try {
      await api.updateReleaseCheck(currentRelease.release_id, editingCheck.check_id, {
        status: editStatus,
        waiver_reason: waiverReason || undefined,
        verified_by: 'lead.release.engineer',
        evidence_details: evidenceDetails || undefined
      });
      setEditingCheck(null);
      loadReleases();
    } catch (err: any) {
      alert(`Failed to update check: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Release Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-indigo-400" />
            Release Reliability & Readiness Engine
          </h2>
          <p className="text-xs text-slate-400">
            Objective release gates evaluated against actual test executions, blocker defects, and database validations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-mono text-slate-400">SELECT RELEASE:</label>
          <select
            value={selectedReleaseId}
            onChange={(e) => {
              setSelectedReleaseId(e.target.value);
              setEvaluationResult(null);
            }}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono font-medium focus:outline-none focus:border-indigo-500"
          >
            {releases.map((r) => (
              <option key={r.release_id} value={r.release_id}>
                {r.release_id} ({r.version_tag}) — {r.status}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-slate-400 text-xs">Loading release metadata...</div>
      ) : !currentRelease ? (
        <div className="text-center py-8 text-slate-400 text-xs">No release record selected.</div>
      ) : (
        <div className="space-y-6">
          {/* Release Readiness Score Card */}
          <div className="p-6 rounded-xl bg-[#0e1526] border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-sm">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2.5">
                <span className="text-lg font-bold text-white font-mono">{currentRelease.version_tag}</span>
                <span
                  className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold ${
                    currentRelease.status === 'RELEASED'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : currentRelease.status === 'READY_FOR_REVIEW'
                      ? 'bg-blue-950 text-blue-300 border border-blue-800'
                      : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}
                >
                  {currentRelease.status}
                </span>
                {currentRelease.is_ready ? (
                  <span className="flex items-center gap-1 text-emerald-400 text-xs font-medium">
                    <CheckCircle2 className="h-4 w-4" /> Release Gates Passed
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-rose-400 text-xs font-medium">
                    <XCircle className="h-4 w-4" /> Gates Blocked
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">{currentRelease.summary}</p>
              {currentRelease.rollback_plan && (
                <div className="text-[11px] text-slate-400 font-mono pt-1">
                  <span className="text-slate-500 uppercase">Rollback Strategy:</span> {currentRelease.rollback_plan}
                </div>
              )}
            </div>

            {/* Score Progress Meter */}
            <div className="flex flex-col items-center md:items-end gap-2 shrink-0">
              <div className="text-center md:text-right">
                <div className="text-3xl font-bold font-mono text-white">
                  {currentRelease.readiness_score}%
                </div>
                <span className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">
                  Objective Readiness Score
                </span>
              </div>
              <button
                disabled={evaluating}
                onClick={handleEvaluate}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-2 transition disabled:opacity-50 shadow-sm"
              >
                {evaluating ? (
                  <>
                    <Activity className="h-3.5 w-3.5 animate-spin" />
                    Evaluating gate criteria...
                  </>
                ) : (
                  <>
                    <Play className="h-3 w-3 fill-current" />
                    Evaluate Release Readiness Engine
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Evaluation Engine Blocking Reasons Callout */}
          {evaluationResult && evaluationResult.blocking_reasons && (
            <div
              className={`p-4 rounded-xl border text-xs space-y-2 ${
                evaluationResult.is_ready
                  ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                  : 'bg-rose-950/20 border-rose-800/40 text-rose-300'
              }`}
            >
              <div className="flex items-center gap-2 font-semibold">
                {evaluationResult.is_ready ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-rose-400" />
                )}
                <span>
                  {evaluationResult.is_ready
                    ? 'All release gates satisfied. Release is cleared for staging validation.'
                    : 'Release Readiness Engine flagged blocking items:'}
                </span>
              </div>
              {!evaluationResult.is_ready && (
                <ul className="list-disc list-inside space-y-1 pl-2 text-rose-200">
                  {evaluationResult.blocking_reasons.map((r: string, idx: number) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Release Checks Table */}
          <div className="rounded-xl bg-[#0e1526] border border-slate-800/80 overflow-hidden">
            <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
              <div>
                <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
                  Mandatory & Supporting Release Checks ({currentRelease.checks?.length ?? 0})
                </h3>
                <p className="text-[11px] text-slate-400">
                  All mandatory checks must be PASSED or explicitly WAIVED with documentation
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[11px] font-mono text-slate-400 uppercase border-b border-slate-800 bg-slate-900/40">
                  <tr>
                    <th className="py-2.5 px-3">Check Name</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Mandatory</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Verification Evidence</th>
                    <th className="py-2.5 px-3">Verified By</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {currentRelease.checks?.map((chk) => (
                    <tr key={chk.check_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-3 font-medium text-slate-200">{chk.check_name}</td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-400">{chk.check_category}</td>
                      <td className="py-3 px-3">
                        {chk.is_mandatory ? (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800">
                            REQUIRED
                          </span>
                        ) : (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                            OPTIONAL
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            chk.status === 'PASSED'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : chk.status === 'FAILED'
                              ? 'bg-rose-950 text-rose-300 border border-rose-800'
                              : chk.status === 'WAIVED'
                              ? 'bg-purple-950 text-purple-300 border border-purple-800'
                              : 'bg-slate-800 text-amber-400 border border-amber-800/50'
                          }`}
                        >
                          {chk.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-300 max-w-xs truncate text-[11px]">
                        {chk.waiver_reason ? (
                          <span className="text-purple-300 italic">Waived: {chk.waiver_reason}</span>
                        ) : (
                          chk.evidence_details || 'Awaiting verification pass'
                        )}
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-400">{chk.verified_by || '—'}</td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => {
                            setEditingCheck(chk);
                            setEditStatus(chk.status);
                            setWaiverReason(chk.waiver_reason || '');
                            setEvidenceDetails(chk.evidence_details || '');
                          }}
                          className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline"
                        >
                          Update Check
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Update Check Modal */}
      {editingCheck && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-md p-5 space-y-4 shadow-2xl text-xs">
            <h3 className="text-sm font-semibold text-white">Update Release Check Status</h3>
            <p className="text-slate-400 font-medium">{editingCheck.check_name}</p>

            <div className="space-y-3">
              <div>
                <label className="block text-slate-400 mb-1">Check Status *</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value as any)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                >
                  <option value="PASSED">PASSED</option>
                  <option value="FAILED">FAILED</option>
                  <option value="PENDING">PENDING</option>
                  <option value="WAIVED">WAIVED (Requires waiver reason)</option>
                </select>
              </div>

              {editStatus === 'WAIVED' && (
                <div>
                  <label className="block text-amber-300 mb-1">Explicit Waiver Reason *</label>
                  <textarea
                    rows={2}
                    placeholder="Document justification for waiving mandatory release check..."
                    value={waiverReason}
                    onChange={(e) => setWaiverReason(e.target.value)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  />
                </div>
              )}

              <div>
                <label className="block text-slate-400 mb-1">Evidence / Verification Notes</label>
                <textarea
                  rows={3}
                  placeholder="Reference test run ID, artifact, or log proof..."
                  value={evidenceDetails}
                  onChange={(e) => setEvidenceDetails(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setEditingCheck(null)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCheck}
                className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
              >
                Save & Recalculate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
