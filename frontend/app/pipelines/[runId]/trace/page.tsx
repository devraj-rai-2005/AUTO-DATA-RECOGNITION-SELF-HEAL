"use client";
import { useEffect, useState, use } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { AgentTraceRow } from "@/lib/types";
import { readableAgentName } from "@/lib/status-style";
import { Skeleton } from "@/lib/skeleton";

export default function TracePage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = use(params);
  const [trace, setTrace] = useState<AgentTraceRow[] | null>(null);

  useEffect(() => { api.getTrace(runId).then(setTrace); }, [runId]);

  const totalMs = trace?.reduce((sum, t) => sum + (t.duration_ms || 0), 0) ?? 0;
  const totalPromptTok = trace?.reduce((sum, t) => sum + (t.prompt_tokens || 0), 0) ?? 0;
  const totalCompletionTok = trace?.reduce((sum, t) => sum + (t.completion_tokens || 0), 0) ?? 0;

  return (
    <div className="min-h-screen">
      <header className="border-b border-hairline px-8 py-5">
        <Link href="/dashboard" className="text-sm text-fog hover:text-paper transition-colors">← Pipeline Healer</Link>
      </header>

      <main className="px-8 py-10 max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-lg font-semibold font-mono">run {runId.slice(0, 8)}</h1>
          <p className="text-sm text-fog mt-1">agent execution trace</p>
        </div>

        {!trace ? (
          <div className="space-y-2">
            <Skeleton className="h-11 w-full" />
            <Skeleton className="h-11 w-full" />
            <Skeleton className="h-11 w-full" />
          </div>
        ) : (
          <>
            <div className="border border-hairline rounded-sm divide-y divide-hairline overflow-hidden">
              {trace.map((t) => (
                <div key={t.id} className="flex items-center justify-between px-4 py-3 font-mono text-sm">
                  <span>{readableAgentName(t.agent_name)}</span>
                  <div className="flex gap-6 text-fog">
                    <span>{t.duration_ms != null ? `${t.duration_ms}ms` : "—"}</span>
                    <span>{(t.prompt_tokens ?? 0) + (t.completion_tokens ?? 0)} tok</span>
                  </div>
                </div>
              ))}
              {trace.length === 0 && <p className="px-4 py-8 text-sm text-fog">No trace data for this run.</p>}
            </div>
            <div className="flex gap-8 font-mono text-sm text-fog pt-1">
              <span>total {totalMs}ms</span>
              <span>{totalPromptTok} prompt tok</span>
              <span>{totalCompletionTok} completion tok</span>
            </div>
          </>
        )}
      </main>
    </div>
  );
}