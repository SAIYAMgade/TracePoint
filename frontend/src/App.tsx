import React, { useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { DefectsPage } from './pages/DefectsPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { RegressionTestsPage } from './pages/RegressionTestsPage';
import { TestRunsPage } from './pages/TestRunsPage';
import { ReleaseReadinessPage } from './pages/ReleaseReadinessPage';
import { DatabaseChangesPage } from './pages/DatabaseChangesPage';
import { AuditPage } from './pages/AuditPage';
import { TracePointLabPage } from './pages/TracePointLabPage';
import { HealthPage } from './pages/HealthPage';

export function App() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [activeDefectId, setActiveDefectId] = useState<string>('DEF-101');
  const [runnerCommand, setRunnerCommand] = useState<string>('pytest demo_lab/tests/test_scenario_a_date_boundary.py -v');
  const [defectFilter, setDefectFilter] = useState<{ status?: string; severity?: string } | undefined>(undefined);

  const handleNavigateFromOverview = (tab: string, filter?: { status?: string; severity?: string }) => {
    if (filter) {
      setDefectFilter(filter);
    }
    setCurrentTab(tab);
  };

  const handleOpenInvestigation = (defectId: string) => {
    setActiveDefectId(defectId);
    setCurrentTab('investigations');
  };

  const handleRunTest = (commandOrTestId?: string, defectId?: string) => {
    if (commandOrTestId) {
      if (commandOrTestId.startsWith('pytest')) {
        setRunnerCommand(commandOrTestId);
      } else {
        // Find matching test command or fallback
        setRunnerCommand(`pytest demo_lab/tests/test_scenario_a_date_boundary.py -v`);
      }
    }
    if (defectId) setActiveDefectId(defectId);
    setCurrentTab('test-runs');
  };

  return (
    <AppLayout currentTab={currentTab} onTabChange={setCurrentTab}>
      {currentTab === 'overview' && (
        <OverviewPage onNavigate={handleNavigateFromOverview} />
      )}
      {currentTab === 'defects' && (
        <DefectsPage
          onOpenInvestigation={handleOpenInvestigation}
          initialFilter={defectFilter}
        />
      )}
      {currentTab === 'investigations' && (
        <InvestigationPage
          initialDefectId={activeDefectId}
          onNavigateToTest={handleRunTest}
        />
      )}
      {currentTab === 'regression-tests' && (
        <RegressionTestsPage onRunTest={handleRunTest} />
      )}
      {currentTab === 'test-runs' && (
        <TestRunsPage
          initialCommand={runnerCommand}
          initialDefectId={activeDefectId}
        />
      )}
      {currentTab === 'releases' && <ReleaseReadinessPage />}
      {currentTab === 'db-changes' && <DatabaseChangesPage />}
      {currentTab === 'audit' && <AuditPage />}
      {currentTab === 'lab' && (
        <TracePointLabPage onNavigateToTest={handleRunTest} />
      )}
      {currentTab === 'health' && <HealthPage />}
    </AppLayout>
  );
}

export default App;
