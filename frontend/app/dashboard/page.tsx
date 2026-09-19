"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useRunEvents } from "@/lib/useRunEvents";
import { statusStripe, statusDot, readableStatus, readableAgentName } from "@/lib/status-style";
import type { PipelineRun, IncidentSummary, FailureType } from "@/lib/types";

const FAILURE_TYPES: { value: FailureType; label: string; description: string }[] = [
  { value: "column_rename", label: "Column rename", description: "A column is silently renamed upstream." },
  { value: "unexpected_nulls", label: "Unexpected NULLs", description: "A previously clean column starts arriving empty." },
  { value: "datetime_drift", label: "Datetime drift", description: "A date column changes format without notice." },
];

export default function DashboardPage() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [triggering, setTriggering] = useState(false);
  const events = useRunEvents(activeRunId);

  const refresh = async () => {
    const [r, i] = await Promise.all([api.listRuns(), api.listIncidents()]);
    setRuns(r);
    setIncidents(i);
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleTrigger = async (failureType: FailureType) => {
    setTriggering(true);
    try {
      const { run_id } = await api.triggerPipeline(failureType);
      setActiveRunId(run_id);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-hairline px-8 py-5 flex items-center justify-between">
        <h1 className="text-lg font-semibold">Pipeline Healer</h1>
        <div className="flex items-center gap-2 text-sm text-fog">
          <span className="w-2 h-2 rounded-full bg-confirmed" />
          Connected
        </div>
      </header>

      <main className="px-8 py-10 max-w-5xl mx-auto space-y-10">
        <section>
          <h2 className="text-sm text-fog mb-3">Inject a failure</h2>
          <div className="grid sm:grid-cols-3 gap-3">
            {FAILURE_TYPES.map((f) => (
              <button
                key={f.value}
                disabled={triggering}
                onClick={() => handleTrigger(f.value)}
                className="text-left border border-hairline bg-surface hover:border-signal/50 transition-colors rounded-sm px-4 py-4 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <div className="font-medium">{f.label}</div>
                <div className="text-sm text-fog mt-1">{f.description}</div>
              </button>
            ))}
          </div>
        </section>

        {activeRunId && (
          <section className="border border-hairline rounded-sm bg-surface px-5 py-4">
            <h2 className="text-sm text-fog mb-3 font-mono">run {activeRunId.slice(0, 8)}</h2>
            <ul className="space-y-1.5">
              {events.map((e, i) => (
                <li key={i} className="flex items-center justify-between gap-3 font-mono text-sm animate-rise-in">
                  <span className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${statusDot(e.status)}`} />
                    {readableAgentName(e.agent)}
                  </span>
                  <span className="text-fog">{readableStatus(e.status)}</span>
                </li>
              ))}
              {events.length === 0 && <li className="text-sm text-fog">Waiting for agent activity.</li>}
            </ul>
          </section>
        )}

        <div className="grid md:grid-cols-2 gap-8">
          <section>
            <h2 className="text-sm text-fog mb-3">Incidents</h2>
            <div className="border border-hairline rounded-sm divide-y divide-hairline overflow-hidden">
              {incidents.map((inc) => (
                <Link
                  key={inc.id}
                  href={`/incidents/${inc.id}`}
                  className={`flex items-center justify-between px-4 py-3 border-l-2 ${statusStripe(inc.status)} hover:bg-surface/70 transition-colors`}
                >
                  <div>
                    <div className="font-mono text-sm">{inc.affected_table}</div>
                    <div className="text-sm text-fog">
                      {inc.root_cause.replace(/_/g, " ")}, {inc.severity} severity
                    </div>
                  </div>
                  <span className="text-sm text-fog">{readableStatus(inc.status)}</span>
                </Link>
              ))}
              {incidents.length === 0 && (
                <p className="px-4 py-8 text-sm text-fog">
                  No incidents yet. Trigger a failure above to see one appear here.
                </p>
              )}
            </div>
          </section>

          <section>
            <h2 className="text-sm text-fog mb-3">Recent runs</h2>
            <div className="border border-hairline rounded-sm divide-y divide-hairline overflow-hidden">
              {runs.map((run) => (
                <div key={run.id} className={`flex items-center justify-between px-4 py-3 border-l-2 ${statusStripe(run.status)}`}>
                  <div className="font-mono text-sm">{run.table_name}</div>
                  <span className="text-sm text-fog">{readableStatus(run.status)}</span>
                </div>
              ))}
              {runs.length === 0 && <p className="px-4 py-8 text-sm text-fog">No runs yet.</p>}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}