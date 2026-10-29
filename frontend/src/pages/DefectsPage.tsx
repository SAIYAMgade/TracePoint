import React, { useEffect, useState } from 'react';
import {
  Bug,
  Search,
  Filter,
  Plus,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  FileText,
  User,
  Tag,
  Microscope,
  CheckCircle2,
  XCircle,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { Defect, DefectStatus, Severity, Priority } from '../types';

interface DefectsPageProps {
  onOpenInvestigation: (defectId: string) => void;
  initialFilter?: { status?: string; severity?: string };
}

export const DefectsPage: React.FC<DefectsPageProps> = ({ onOpenInvestigation, initialFilter }) => {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>(initialFilter?.severity || '');
  const [statusFilter, setStatusFilter] = useState<string>(initialFilter?.status || '');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Selected Defect for Drawer / Modal
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);

  // Transition Modal State
  const [transitioning, setTransitioning] = useState(false);
  const [targetStatus, setTargetStatus] = useState<string>('REPRODUCED');
  const [transitionActor, setTransitionActor] = useState('alex.chen');
  const [transitionReason, setTransitionReason] = useState('');
  const [transitionError, setTransitionError] = useState<string | null>(null);

  // Create Defect Modal
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSeverity, setNewSeverity] = useState<Severity>('HIGH');
  const [newPriority, setNewPriority] = useState<Priority>('P1');
  const [newComponent, setNewComponent] = useState('');
  const [newEnv, setNewEnv] = useState('STAGING');
  const [newOwner, setNewOwner] = useState('alex.chen');

  const loadDefects = () => {
    setLoading(true);
    api.getDefects({
      skip: (page - 1) * pageSize,
      limit: pageSize,
      severity: severityFilter || undefined,
      status: statusFilter || undefined,
      search: search || undefined
    })
      .then((res) => {
        setDefects(res.items);
        setTotal(res.total);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDefects();
  }, [page, severityFilter, statusFilter, search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api.createDefect({
        title: newTitle,
        description: newDesc,
        severity: newSeverity,
        priority: newPriority,
        affected_component: newComponent || 'core-engine',
        environment: newEnv,
        assigned_owner: newOwner
      });
      setIsCreating(false);
      setNewTitle('');
      setNewDesc('');
      loadDefects();
      setSelectedDefect(created);
    } catch (err: any) {
      alert(`Failed to create defect: ${err.message}`);
    }
  };

  const handleTransition = async () => {
    if (!selectedDefect) return;
    setTransitionError(null);
    try {
      const updated = await api.transitionDefect(
        selectedDefect.defect_id,
        targetStatus,
        transitionActor,
        transitionReason || 'State transition requested by engineer'
      );
      setSelectedDefect(updated);
      setTransitioning(false);
      setTransitionReason('');
      loadDefects();
    } catch (err: any) {
      setTransitionError(err.message);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <Bug className="h-5 w-5 text-indigo-400" />
            Defect Registry & State Machine
          </h2>
          <p className="text-xs text-slate-400">
            Enforced lifecycle transitions, verified evidence requirements, and regression test linkage.
          </p>
        </div>

        <button
          onClick={() => setIsCreating(true)}
          className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 transition self-start sm:self-auto shadow-sm"
        >
          <Plus className="h-4 w-4" />
          Log New Defect
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-3 rounded-lg bg-[#0e1526] border border-slate-800 flex flex-wrap items-center gap-3 text-xs">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="h-3.5 w-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search defects by ID, title, or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Severity Filter */}
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="REPRODUCED">Reproduced</option>
          <option value="INVESTIGATING">Investigating</option>
          <option value="FIX_PROPOSED">Fix Proposed</option>
          <option value="VALIDATION_REQUIRED">Validation Required</option>
          <option value="VERIFIED">Verified</option>
          <option value="CLOSED">Closed</option>
        </select>

        {(severityFilter || statusFilter || search) && (
          <button
            onClick={() => {
              setSeverityFilter('');
              setStatusFilter('');
              setSearch('');
            }}
            className="text-xs text-slate-400 hover:text-slate-200 underline"
          >
            Reset Filters
          </button>
        )}
      </div>

      {/* Defects Data Table */}
      <div className="rounded-xl bg-[#0e1526] border border-slate-800/80 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[11px] font-mono text-slate-400 uppercase border-b border-slate-800 bg-slate-900/60">
              <tr>
                <th className="py-2.5 px-3">Defect ID</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Title & Summary</th>
                <th className="py-2.5 px-3">Component</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Reproduction</th>
                <th className="py-2.5 px-3">Verification</th>
                <th className="py-2.5 px-3">Owner</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 text-xs">
                    Loading defects from database...
                  </td>
                </tr>
              ) : defects.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 text-xs">
                    No defects found matching current filters.
                  </td>
                </tr>
              ) : (
                defects.map((d) => (
                  <tr
                    key={d.defect_id}
                    onClick={() => setSelectedDefect(d)}
                    className="hover:bg-slate-800/40 cursor-pointer transition"
                  >
                    <td className="py-3 px-3 font-mono font-medium text-indigo-400">{d.defect_id}</td>
                    <td className="py-3 px-3">
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
                    <td className="py-3 px-3 max-w-sm">
                      <div className="font-medium text-slate-200 truncate">{d.title}</div>
                      <div className="text-[11px] text-slate-400 truncate">{d.description}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-400 font-mono text-[11px]">{d.affected_component}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded font-mono text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                        {d.status}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                          d.reproduction_status === 'REPRODUCED'
                            ? 'text-emerald-400 bg-emerald-950/40 border border-emerald-800/40'
                            : 'text-amber-400 bg-amber-950/40 border border-amber-800/40'
                        }`}
                      >
                        {d.reproduction_status}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                          d.verification_status === 'VERIFIED'
                            ? 'text-emerald-400 bg-emerald-950/40'
                            : d.verification_status === 'IN_PROGRESS'
                            ? 'text-blue-400 bg-blue-950/40'
                            : 'text-slate-400 bg-slate-800/40'
                        }`}
                      >
                        {d.verification_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-400">{d.assigned_owner}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/40 flex items-center justify-between text-xs text-slate-400">
          <span>Showing {defects.length} of {total} defects</span>
          <div className="flex items-center gap-1">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              Previous
            </button>
            <span className="px-2 font-mono">{page}</span>
            <button
              disabled={page * pageSize >= total}
              onClick={() => setPage((p) => p + 1)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Defect Detail Drawer / Modal */}
      {selectedDefect && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-sm font-bold text-indigo-400">{selectedDefect.defect_id}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                  {selectedDefect.status}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                  {selectedDefect.severity}
                </span>
              </div>
              <button onClick={() => setSelectedDefect(null)} className="text-slate-400 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Content Body */}
            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              <div>
                <h3 className="text-base font-semibold text-white leading-snug">{selectedDefect.title}</h3>
                <p className="text-slate-300 mt-2 leading-relaxed whitespace-pre-line">{selectedDefect.description}</p>
              </div>

              {/* Behavior Breakdown */}
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">Expected Behavior</span>
                  <p className="text-slate-300 text-[11px]">{selectedDefect.expected_behavior || 'Not specified'}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">Actual Behavior</span>
                  <p className="text-rose-300/90 text-[11px]">{selectedDefect.actual_behavior || 'Not specified'}</p>
                </div>
              </div>

              {/* Root Cause & Correction */}
              {selectedDefect.root_cause_explanation && (
                <div className="p-3 rounded-lg bg-purple-950/20 border border-purple-800/40">
                  <span className="text-[10px] font-mono uppercase text-purple-400 font-semibold block mb-1">
                    Confirmed Root Cause
                  </span>
                  <p className="text-purple-200 text-xs">{selectedDefect.root_cause_explanation}</p>
                </div>
              )}

              {selectedDefect.proposed_correction && (
                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40">
                  <span className="text-[10px] font-mono uppercase text-emerald-400 font-semibold block mb-1">
                    Proposed Correction
                  </span>
                  <p className="text-emerald-200 text-xs">{selectedDefect.proposed_correction}</p>
                </div>
              )}

              {/* Metadata Grid */}
              <div className="grid grid-cols-3 gap-2 text-[11px] font-mono text-slate-400">
                <div>
                  <span className="text-slate-500 block">COMPONENT</span>
                  <span className="text-slate-200">{selectedDefect.affected_component}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">ENVIRONMENT</span>
                  <span className="text-slate-200">{selectedDefect.environment}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">OWNER</span>
                  <span className="text-slate-200">{selectedDefect.assigned_owner}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">REPRO STATUS</span>
                  <span className="text-emerald-400">{selectedDefect.reproduction_status}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">VERIF STATUS</span>
                  <span className="text-indigo-400">{selectedDefect.verification_status}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">TARGET RELEASE</span>
                  <span className="text-slate-200">{selectedDefect.associated_release_id || 'None'}</span>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between gap-3">
              <button
                onClick={() => {
                  const defId = selectedDefect.defect_id;
                  setSelectedDefect(null);
                  onOpenInvestigation(defId);
                }}
                className="px-3 py-1.5 rounded-lg bg-purple-600/20 border border-purple-500/40 text-purple-300 text-xs font-medium hover:bg-purple-600/30 transition flex items-center gap-1.5"
              >
                <Microscope className="h-4 w-4" />
                Open Investigation Workspace
              </button>

              <button
                onClick={() => setTransitioning(true)}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm"
              >
                Transition Defect State...
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transition Modal */}
      {transitioning && selectedDefect && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-md p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Execute State Transition</h3>
              <button onClick={() => setTransitioning(false)} className="text-slate-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="text-xs text-slate-400">
              Current Status: <span className="text-indigo-400 font-mono font-bold">{selectedDefect.status}</span>
            </div>

            {transitionError && (
              <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-start gap-2">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{transitionError}</span>
              </div>
            )}

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Target Status</label>
                <select
                  value={targetStatus}
                  onChange={(e) => setTargetStatus(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                >
                  <option value="REPRODUCED">REPRODUCED</option>
                  <option value="INVESTIGATING">INVESTIGATING</option>
                  <option value="FIX_PROPOSED">FIX_PROPOSED</option>
                  <option value="VALIDATION_REQUIRED">VALIDATION_REQUIRED</option>
                  <option value="VERIFIED">VERIFIED (Requires verification evidence)</option>
                  <option value="CLOSED">CLOSED</option>
                  <option value="REJECTED">REJECTED</option>
                  <option value="DUPLICATE">DUPLICATE</option>
                  <option value="INCONCLUSIVE">INCONCLUSIVE</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Engineer / Actor</label>
                <input
                  type="text"
                  value={transitionActor}
                  onChange={(e) => setTransitionActor(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Transition Reason / Evidence Reference</label>
                <textarea
                  rows={3}
                  value={transitionReason}
                  onChange={(e) => setTransitionReason(e.target.value)}
                  placeholder="State the objective reason or verification evidence for this transition..."
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setTransitioning(false)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
              >
                Cancel
              </button>
              <button
                onClick={handleTransition}
                className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm"
              >
                Confirm Transition
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Defect Modal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-lg p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Log Defect for Engineering Investigation</h3>
              <button type="button" onClick={() => setIsCreating(false)} className="text-slate-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Defect Title *</label>
                <input
                  required
                  type="text"
                  placeholder="Concise defect statement (e.g. Query omits midnight boundary records)"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Description *</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Detailed description of symptoms, affected environment, and impact..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Severity</label>
                  <select
                    value={newSeverity}
                    onChange={(e) => setNewSeverity(e.target.value as Severity)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value as Priority)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  >
                    <option value="P1">P1</option>
                    <option value="P2">P2</option>
                    <option value="P3">P3</option>
                    <option value="P4">P4</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Component</label>
                  <input
                    type="text"
                    value={newComponent}
                    onChange={(e) => setNewComponent(e.target.value)}
                    placeholder="e.g. billing-service"
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Assigned Owner</label>
                  <input
                    type="text"
                    value={newOwner}
                    onChange={(e) => setNewOwner(e.target.value)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm"
              >
                Submit Defect Record
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
