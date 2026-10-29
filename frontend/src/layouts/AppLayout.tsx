import React, { useEffect, useState } from 'react';
import {
  LayoutDashboard,
  Bug,
  Microscope,
  FileCheck2,
  PlaySquare,
  ShieldAlert,
  Database,
  History,
  FlaskConical,
  Activity,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api/client';
import { SystemHealth } from '../types';

interface AppLayoutProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ currentTab, onTabChange, children }) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch((err) => console.error('Failed to load health:', err));
  }, []);

  const navItems = [
    { id: 'overview', label: 'Engineering Overview', icon: LayoutDashboard },
    { id: 'defects', label: 'Defect Registry', icon: Bug },
    { id: 'investigations', label: 'Investigation Workspace', icon: Microscope },
    { id: 'regression-tests', label: 'Regression Tests', icon: FileCheck2 },
    { id: 'test-runs', label: 'Test Runs & Runner', icon: PlaySquare },
    { id: 'releases', label: 'Release Readiness', icon: ShieldAlert },
    { id: 'db-changes', label: 'DB Change Validation', icon: Database },
    { id: 'audit', label: 'Audit History', icon: History },
    { id: 'lab', label: 'TracePoint Lab', icon: FlaskConical },
    { id: 'health', label: 'System Health', icon: Activity },
  ];

  const isOracle = health?.database?.is_oracle ?? false;

  return (
    <div className="flex min-h-screen bg-[#080c14] text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-[#0c1220] flex flex-col justify-between shrink-0">
        <div>
          {/* Logo / Header */}
          <div className="p-4 border-b border-slate-800/80">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 font-bold tracking-tight">
                TP
              </div>
              <div>
                <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-1.5">
                  TracePoint
                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                    ASE-1
                  </span>
                </h1>
                <p className="text-[11px] text-slate-400">Release Reliability Platform</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-2 space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-all ${
                    active
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`h-4 w-4 shrink-0 ${active ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Database Engine Status Pill */}
        <div className="p-3 m-2 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-slate-400 font-mono">DATABASE ENGINE</span>
            {isOracle ? (
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="h-3 w-3" /> Oracle 23ai
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400 font-medium">
                <AlertTriangle className="h-3 w-3" /> SQLite Fallback
              </span>
            )}
          </div>
          <p className="text-slate-400 leading-tight">
            {isOracle
              ? 'Native PL/SQL packages & Oracle constraints active.'
              : 'Zero-config local engine. Oracle PL/SQL DDL & packages exported.'}
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 border-b border-slate-800/80 bg-[#0c1220]/70 backdrop-blur px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              WORKSPACE: <span className="text-slate-200">PRODUCTION READINESS TRIAGE</span>
            </span>
            <span className="h-3 w-[1px] bg-slate-800" />
            <span className="text-xs text-slate-400 font-mono">
              TARGET RELEASE: <span className="text-indigo-400 font-semibold">REL-2026.1.0</span>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onTabChange('lab')}
              className="text-xs px-2.5 py-1.5 rounded bg-purple-900/30 text-purple-300 border border-purple-700/40 hover:bg-purple-900/50 flex items-center gap-1.5 transition"
            >
              <FlaskConical className="h-3.5 w-3.5" />
              TracePoint Lab
            </button>
            <button
              onClick={() => onTabChange('test-runs')}
              className="text-xs px-2.5 py-1.5 rounded bg-indigo-600 text-white font-medium hover:bg-indigo-500 shadow-sm flex items-center gap-1.5 transition"
            >
              <PlaySquare className="h-3.5 w-3.5" />
              Test Runner
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
