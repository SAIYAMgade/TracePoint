import React, { useEffect, useState } from 'react';
import {
  Microscope,
  Clock,
  FileCode2,
  FileText,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Plus,
  ShieldCheck,
  Send,
  User,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { Defect, Investigation, Evidence, InvestigationEvent } from '../types';

interface InvestigationPageProps {
  initialDefectId?: string;
  onNavigateToTest: (testId?: string) => void;
}

export const InvestigationPage: React.FC<InvestigationPageProps> = ({ initialDefectId, onNavigateToTest }) => {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [selectedDefectId, setSelectedDefectId] = useState<string>(initialDefectId || 'DEF-101');
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);

  // Evidence Modal
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [eviTitle, setEviTitle] = useState('');
  const [eviType, setEviType] = useState<Evidence['evidence_type']>('SQL_STATEMENT');
  const [eviCode, setEviCode] = useState('');
  const [eviPayload, setEviPayload] = useState('');
  const [eviCollector, setEviCollector] = useState('alex.chen');

  // Edit Root Cause Modal
  const [showEditModal, setShowEditModal] = useState(false);
  const [confirmedCause, setConfirmedCause] = useState('');
  const [proposedCorrection, setProposedCorrection] = useState('');
  const [verificationPlan, setVerificationPlan] = useState('');

  const loadData = (defId: string) => {
    setLoading(true);
    Promise.all([
      api.getInvestigationByDefect(defId).catch(() => null),
      api.getEvidence(defId).catch(() => [])
    ])
      .then(([inv, evi]) => {
        setInvestigation(inv);
        setEvidenceList(evi);
        if (inv) {
          setConfirmedCause(inv.confirmed_root_cause || '');
          setProposedCorrection(inv.proposed_correction || '');
          setVerificationPlan(inv.verification_plan || '');
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    api.getDefects({ limit: 50 }).then((res) => {
      setDefects(res.items);
      if (!initialDefectId && res.items.length > 0) {
        setSelectedDefectId(res.items[0].defect_id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedDefectId) {
      loadData(selectedDefectId);
    }
  }, [selectedDefectId]);

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.addEvidence(selectedDefectId, {
        investigation_id: investigation?.investigation_id,
        evidence_type: eviType,
        title: eviTitle,
        error_code: eviCode || undefined,
        sanitized_payload: eviPayload,
        collected_by: eviCollector
      });
      setShowEvidenceModal(false);
      setEviTitle('');
      setEviPayload('');
      setEviCode('');
      loadData(selectedDefectId);
    } catch (err: any) {
      alert(`Failed to add evidence: ${err.message}`);
    }
  };

  const handleUpdateInvestigation = async () => {
    if (!investigation) return;
    try {
      await api.updateInvestigation(investigation.investigation_id, {
        confirmed_root_cause: confirmedCause,
        proposed_correction: proposedCorrection,
        verification_plan: verificationPlan,
        status: confirmedCause ? 'ROOT_CAUSE_IDENTIFIED' : 'IN_PROGRESS'
      });
      setShowEditModal(false);
      loadData(selectedDefectId);
    } catch (err: any) {
      alert(`Failed to update investigation: ${err.message}`);
    }
  };

  const selectedDefect = defects.find((d) => d.defect_id === selectedDefectId);

  return (
    <div className="space-y-6">
      {/* Header & Defect Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-[#0e1526] border border-slate-800">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            <Microscope className="h-5 w-5 text-indigo-400" />
            Root-Cause Analysis & Investigation Workspace
          </h2>
          <p className="text-xs text-slate-400">
            Disciplined investigation model: distinguish between Observation, Hypothesis, and Confirmed Cause.
          </p>
        </div>

        {/* Defect Picker Dropdown */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-mono text-slate-400">ACTIVE CASE:</label>
          <select
            value={selectedDefectId}
            onChange={(e) => setSelectedDefectId(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono font-medium focus:outline-none focus:border-indigo-500"
          >
            {defects.map((d) => (
              <option key={d.defect_id} value={d.defect_id}>
                {d.defect_id} — {d.title.substring(0, 45)}...
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48 text-slate-400 text-xs">
          Loading investigation case and timeline events...
        </div>
      ) : !investigation ? (
        <div className="p-8 rounded-xl bg-[#0e1526] border border-slate-800 text-center space-y-3">
          <HelpCircle className="h-8 w-8 mx-auto text-slate-500" />
          <h3 className="text-sm font-semibold text-white">No Investigation Initialized</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            This defect does not currently have an active root-cause investigation record.
          </p>
          <button
            onClick={async () => {
              if (!selectedDefect) return;
              await api.createInvestigation({
                defect_id: selectedDefect.defect_id,
                problem_statement: selectedDefect.description,
                observed_symptoms: selectedDefect.actual_behavior || 'System returned unexpected result.',
                initial_hypothesis: 'Underlying query or logic defect requires code and database inspection.',
                lead_investigator: selectedDefect.assigned_owner
              });
              loadData(selectedDefect.defect_id);
            }}
            className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
          >
            Initialize Investigation Case
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main 3-Concept Workspace (Observation, Hypothesis, Confirmed Cause) */}
          <div className="lg:col-span-2 space-y-4">
            {/* Status and Lead Investigator Banner */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="font-mono text-slate-400">INVESTIGATION ID:</span>
                <span className="font-mono font-bold text-indigo-400">{investigation.investigation_id}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                  {investigation.status}
                </span>
              </div>
              <div className="text-slate-400">
                Lead: <span className="text-slate-200 font-medium">{investigation.lead_investigator}</span>
              </div>
            </div>

            {/* CONCEPT 1: OBSERVATION (What the system actually showed) */}
            <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-semibold text-sky-300">
                <span className="h-2 w-2 rounded-full bg-sky-400" />
                CONCEPT 1: OBSERVATION (What the system actually showed)
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-500 block mb-0.5">Problem Statement</span>
                <p className="text-xs text-slate-200 leading-relaxed">{investigation.problem_statement}</p>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-500 block mb-0.5">Observed Symptoms</span>
                <p className="text-xs text-slate-300/90 leading-relaxed bg-slate-900/60 p-2.5 rounded border border-slate-800">
                  {investigation.observed_symptoms}
                </p>
              </div>
            </div>

            {/* CONCEPT 2: HYPOTHESIS (What might explain the failure) */}
            <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-semibold text-amber-300">
                <span className="h-2 w-2 rounded-full bg-amber-400" />
                CONCEPT 2: HYPOTHESIS (What might explain the failure)
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-500 block mb-0.5">Initial Hypothesis</span>
                <p className="text-xs text-slate-200 leading-relaxed">{investigation.initial_hypothesis}</p>
              </div>
              {investigation.candidate_causes && (
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block mb-0.5">Candidate Root Causes</span>
                  <div className="text-xs text-slate-300/90 whitespace-pre-line bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    {investigation.candidate_causes}
                  </div>
                </div>
              )}
            </div>

            {/* CONCEPT 3: CONFIRMED ROOT CAUSE & CORRECTION */}
            <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-300">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  CONCEPT 3: CONFIRMED ROOT CAUSE & VERIFICATION PLAN
                </div>
                <button
                  onClick={() => setShowEditModal(true)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline"
                >
                  Update Conclusion & Fix
                </button>
              </div>

              {investigation.confirmed_root_cause ? (
                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40 space-y-2 text-xs">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-emerald-400 font-semibold block mb-0.5">
                      Confirmed Root Cause (Supported by Technical Evidence)
                    </span>
                    <p className="text-emerald-200 leading-relaxed">{investigation.confirmed_root_cause}</p>
                  </div>

                  {investigation.proposed_correction && (
                    <div>
                      <span className="text-[10px] font-mono uppercase text-emerald-400 font-semibold block mb-0.5">
                        Proposed Correction
                      </span>
                      <p className="text-slate-200">{investigation.proposed_correction}</p>
                    </div>
                  )}

                  {investigation.verification_plan && (
                    <div>
                      <span className="text-[10px] font-mono uppercase text-emerald-400 font-semibold block mb-0.5">
                        Regression Verification Plan
                      </span>
                      <p className="text-slate-300">{investigation.verification_plan}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-400 text-center">
                  Root cause is not yet confirmed. Awaiting supporting evidence from tests or database execution plans.
                </div>
              )}

              {/* Action: Run associated regression test */}
              {selectedDefect?.associated_regression_test_id && (
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    Linked Regression Test: <span className="text-indigo-400 font-mono font-medium">{selectedDefect.associated_regression_test_id}</span>
                  </span>
                  <button
                    onClick={() => onNavigateToTest(selectedDefect.associated_regression_test_id)}
                    className="px-3 py-1 rounded bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 text-xs font-medium hover:bg-indigo-600/50 transition flex items-center gap-1"
                  >
                    <span>Execute Regression Test</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              )}
            </div>

            {/* Attached Evidence Records */}
            <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
                    Technical Evidence Items ({evidenceList.length})
                  </h3>
                  <p className="text-[11px] text-slate-400">Sanitized SQL statements, logs, execution plans, and test outputs</p>
                </div>
                <button
                  onClick={() => setShowEvidenceModal(true)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium flex items-center gap-1 transition"
                >
                  <Plus className="h-3.5 w-3.5" />
                  Attach Evidence
                </button>
              </div>

              {evidenceList.length === 0 ? (
                <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 text-center text-xs text-slate-500">
                  No technical evidence attached yet.
                </div>
              ) : (
                <div className="space-y-2">
                  {evidenceList.map((e) => (
                    <div key={e.evidence_id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                          <FileCode2 className="h-3.5 w-3.5 text-indigo-400" />
                          {e.title}
                        </span>
                        <div className="flex items-center gap-2">
                          {e.error_code && (
                            <span className="px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 font-mono text-[10px] border border-rose-800">
                              {e.error_code}
                            </span>
                          )}
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono text-[10px]">
                            {e.evidence_type}
                          </span>
                        </div>
                      </div>
                      <pre className="p-2.5 rounded bg-black/50 text-slate-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap border border-slate-800/80">
                        {e.sanitized_payload}
                      </pre>
                      <div className="text-[10px] font-mono text-slate-500 flex items-center justify-between pt-1">
                        <span>Collected by: {e.collected_by}</span>
                        <span>{e.created_at}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Investigation Event Timeline */}
          <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 flex flex-col">
            <div className="flex items-center gap-2 text-xs font-semibold text-white uppercase tracking-wider font-mono mb-4 pb-2 border-b border-slate-800">
              <Clock className="h-4 w-4 text-indigo-400" />
              Investigation Timeline ({investigation.events?.length ?? 0} Events)
            </div>

            <div className="space-y-4 relative before:absolute before:inset-0 before:left-2 before:w-0.5 before:bg-slate-800 overflow-y-auto max-h-[650px] pr-2">
              {investigation.events?.map((evt, idx) => (
                <div key={evt.event_id || idx} className="relative pl-6 text-xs space-y-1">
                  <div className="absolute left-0.5 top-1.5 h-3 w-3 rounded-full bg-indigo-600 border-2 border-[#0e1526]" />
                  <div className="flex items-baseline justify-between">
                    <span className="font-semibold text-slate-200 text-xs">{evt.title}</span>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800/60 font-mono text-[10px] text-indigo-300 border border-slate-700/50 inline-block">
                    {evt.event_type}
                  </span>
                  {evt.details && <p className="text-slate-400 text-[11px] leading-relaxed">{evt.details}</p>}
                  <div className="text-[10px] font-mono text-slate-500 flex items-center justify-between pt-0.5">
                    <span>Actor: {evt.actor}</span>
                    <span>{evt.created_at}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Attach Evidence Modal */}
      {showEvidenceModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <form onSubmit={handleAddEvidence} className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-md p-5 space-y-4 shadow-2xl">
            <h3 className="text-sm font-semibold text-white">Attach Technical Evidence</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Evidence Title *</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Oracle ORA-02291 Constraint Trace"
                  value={eviTitle}
                  onChange={(e) => setEviTitle(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Evidence Type</label>
                  <select
                    value={eviType}
                    onChange={(e) => setEviType(e.target.value as any)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  >
                    <option value="SQL_STATEMENT">SQL Statement</option>
                    <option value="ERROR_LOG">Error Log</option>
                    <option value="STACK_TRACE">Stack Trace</option>
                    <option value="TEST_OUTPUT">Test Output</option>
                    <option value="CODE_DIFF">Code Diff</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Error Code (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. ORA-02291"
                    value={eviCode}
                    onChange={(e) => setEviCode(e.target.value)}
                    className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Sanitized Technical Content *</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Paste sanitized technical payload..."
                  value={eviPayload}
                  onChange={(e) => setEviPayload(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowEvidenceModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
              >
                Save Evidence
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Edit Root Cause Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e1526] border border-slate-800 rounded-xl w-full max-w-lg p-5 space-y-4 shadow-2xl">
            <h3 className="text-sm font-semibold text-white">Record Confirmed Root Cause & Verification Plan</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Confirmed Root Cause Explanation</label>
                <textarea
                  rows={3}
                  placeholder="State the confirmed mechanism supported by evidence..."
                  value={confirmedCause}
                  onChange={(e) => setConfirmedCause(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Proposed Code or SQL Correction</label>
                <textarea
                  rows={2}
                  placeholder="Detail the code/query fix..."
                  value={proposedCorrection}
                  onChange={(e) => setProposedCorrection(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Verification Plan & Regression Test</label>
                <textarea
                  rows={2}
                  placeholder="Automated test suite or verification query..."
                  value={verificationPlan}
                  onChange={(e) => setVerificationPlan(e.target.value)}
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUpdateInvestigation}
                className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium"
              >
                Save Root Cause Findings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
