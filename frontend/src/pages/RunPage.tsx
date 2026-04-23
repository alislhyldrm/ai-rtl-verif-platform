import { useParams, useNavigate } from "react-router-dom";
import { useVerificationRun } from "@/hooks/useVerificationRun";
import { IterationStepper } from "@/components/run/IterationStepper";
import { LogViewer } from "@/components/run/LogViewer";
import { CoveragePanel } from "@/components/run/CoveragePanel";
import { TestCodeViewer } from "@/components/run/TestCodeViewer";
import { Button } from "@/components/ui/button";
import { cancelRun } from "@/api/client";
import { X } from "lucide-react";

export function RunPage() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const run = useVerificationRun(runId!);

  async function handleCancel() {
    await cancelRun(runId!);
    navigate("/");
  }

  const latestPct = run.coverageHistory.at(-1) ?? 0;

  return (
    <div className="max-w-3xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Verification Run</h1>
          <p className="text-xs text-[hsl(var(--muted-foreground))] font-mono">{runId}</p>
        </div>
        {run.status !== "done" && (
          <Button variant="destructive" size="sm" onClick={handleCancel} className="gap-1">
            <X className="h-4 w-4" /> Cancel
          </Button>
        )}
      </div>

      <IterationStepper
        iteration={run.currentIteration}
        maxIterations={10}
        phase={run.currentPhase}
        status={run.status}
      />

      <div className="grid grid-cols-2 gap-4">
        <CoveragePanel
          pct={latestPct}
          target={90}
          history={run.coverageHistory}
          gaps={run.gaps}
        />
        <LogViewer lines={run.logs} />
      </div>

      {run.testUrls.size > 0 && (
        <TestCodeViewer runId={runId!} testUrls={run.testUrls} />
      )}

      {run.status === "done" && run.finalReport && (
        <div className="rounded-lg border border-[hsl(var(--border))] p-4 text-sm">
          <p className="font-medium mb-1">
            {run.finalReport.target_reached ? "✓ Target reached" : "✗ Target not reached"}
          </p>
          <p className="text-[hsl(var(--muted-foreground))]">
            Final coverage: {run.finalReport.final_pct.toFixed(1)}% over{" "}
            {run.finalReport.iterations} iteration(s)
          </p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => navigate("/")}>
            New run
          </Button>
        </div>
      )}
    </div>
  );
}
