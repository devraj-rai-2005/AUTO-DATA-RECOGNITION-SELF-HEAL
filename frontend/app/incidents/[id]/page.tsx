"use client";
import {useEffect, useState,  } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IncidentDetail } from "@/lib/types";
import { Textarea } from "@/components/ui/textarea";
import { statusStripe, statusDot, readableStatus } from "@/lib/status-style";
import { Skeleton } from "@/lib/skeleton";

function SqlBlock({ title, sql }: { title: string; sql: string | null }) {
  return (
    <div>
      <p className="text-sm text-fog mb-1.5">{title}</p>
      <pre className="font-mono text-xs bg-surface border border-hairline rounded-sm p-4 overflow-x-auto whitespace-pre-wrap leading-relaxed">
        {sql || "No SQL available for this root cause."}
      </pre>
    </div>
  );
}

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState<"approve" | "reject" | "changes" | null>(null);

  const load = async () => setIncident(await api.getIncident(id));
  useEffect(() => { load(); }, [id]);

  useEffect(() => {
    if (!incident || incident.status === "applied" || incident.status === "rejected") return;
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, [incident?.status]);

  if (!incident) {
    return (
      <div className="min-h-screen">
        <header className="border-b border-hairline px-8 py-5">
          <Link href="/dashboard" className="text-sm text-fog">← Pipeline Healer</Link>
        </header>
        <main className="px-8 py-10 max-w-3xl mx-auto space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-48 w-full" />
        </main>
      </div>
    );
  }

  const decided = incident.status !== "pending_review";

  const handleDecision = async (approved: boolean, tag: "approve" | "reject" | "changes") => {
    setSubmitting(tag);
    try {
      await api.decideIncident(id, approved, notes);
      await load();
    } finally {
      setSubmitting(null);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-hairline px-8 py-5 flex items-center justify-between">
        <Link href="/dashboard" className="text-sm text-fog hover:text-paper transition-colors">← Pipeline Healer</Link>
        <Link href={`/pipelines/${incident.pipeline_run_id}/trace`} className="text-sm text-fog hover:text-paper transition-colors">
          View agent trace
        </Link>
      </header>

      <main className="px-8 py-10 max-w-3xl mx-auto space-y-8">
        <div className={`flex items-center justify-between border-l-2 pl-4 ${statusStripe(incident.status)}`}>
          <div>
            <h1 className="text-xl font-semibold font-mono">{incident.affected_table}</h1>
            <p className="text-sm text-fog mt-1">{incident.root_cause.replace(/_/g, " ")}, {incident.severity} severity</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-fog">
            <span className={`w-1.5 h-1.5 rounded-full ${statusDot(incident.status)}`} />
            {readableStatus(incident.status)}
          </div>
        </div>

        <section>
          <p className="text-sm text-fog mb-1.5">Root cause</p>
          <p className="leading-relaxed">{incident.explanation}</p>
        </section>

        <section className="border border-hairline rounded-sm bg-surface/50 p-5 space-y-3">
          <p className="text-sm text-fog">Sandbox dry-run</p>
          <div className="flex gap-8 font-mono text-sm">
            <span>rows before <span className="text-paper">{incident.rows_before ?? "—"}</span></span>
            <span>rows after <span className="text-paper">{incident.rows_after ?? "—"}</span></span>
          </div>
          {incident.dry_run_notes && <p className="text-sm text-fog">{incident.dry_run_notes}</p>}
          {incident.changed_sample && incident.changed_sample.length > 0 && (
            <div className="font-mono text-xs bg-ink border border-hairline rounded-sm p-3 overflow-x-auto">
              {incident.changed_sample.map((row, i) => <div key={i}>{row}</div>)}
            </div>
          )}
        </section>

        <section className="space-y-4">
          <SqlBlock title="Migration" sql={incident.migration_sql} />
          <SqlBlock title="Rollback" sql={incident.rollback_sql} />
        </section>

        {!decided ? (
          <section className="space-y-3">
            <p className="text-sm text-fog">Review decision</p>
            <Textarea
              placeholder="Reviewer notes (recorded in the audit log)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="bg-surface border-hairline"
            />
            <div className="flex gap-3">
              <button
                disabled={!!submitting}
                onClick={() => handleDecision(true, "approve")}
                className="px-4 py-2 rounded-sm border border-confirmed/40 text-confirmed hover:bg-confirmed/10 transition-colors disabled:opacity-40"
              >
                {submitting === "approve" ? "Applying…" : "Approve"}
              </button>
              <button
                disabled={!!submitting}
                onClick={() => handleDecision(false, "reject")}
                className="px-4 py-2 rounded-sm border border-alarm/40 text-alarm hover:bg-alarm/10 transition-colors disabled:opacity-40"
              >
                {submitting === "reject" ? "Rejecting…" : "Reject"}
              </button>
              <button
                disabled={!!submitting || !notes}
                onClick={() => handleDecision(false, "changes")}
                className="px-4 py-2 rounded-sm border border-signal/40 text-signal hover:bg-signal/10 transition-colors disabled:opacity-40"
              >
                Request changes
              </button>
            </div>
          </section>
        ) : (
          <p className="text-sm text-fog">Decision recorded. Status: {readableStatus(incident.status)}.</p>
        )}
      </main>
    </div>
  );
}