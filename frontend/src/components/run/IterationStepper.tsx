import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle } from "lucide-react";

const PHASES = ["generating", "simulating", "analyzing"] as const;
type Phase = (typeof PHASES)[number];

interface Props {
  iteration: number;
  maxIterations: number;
  phase: string;
  status: string;
}

export function IterationStepper({ iteration, maxIterations, phase, status }: Props) {
  if (iteration === 0) return null;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          Iteration {iteration} / {maxIterations}
        </p>
        {status === "done" ? (
          <Badge variant="outline" className="text-green-400 border-green-400">Done</Badge>
        ) : (
          <Badge variant="secondary">{status}</Badge>
        )}
      </div>
      <div className="flex gap-2">
        {PHASES.map((p) => {
          const idx = PHASES.indexOf(p as Phase);
          const current = PHASES.indexOf(phase as Phase);
          const past = status === "done" || idx < current;
          const active = idx === current && status !== "done";
          return (
            <div
              key={p}
              className={`flex-1 rounded px-2 py-1 text-xs text-center flex items-center justify-center gap-1
                ${past ? "bg-[hsl(var(--primary))]/20 text-[hsl(var(--primary))]" : ""}
                ${active ? "bg-[hsl(var(--muted))] text-[hsl(var(--foreground))] border border-[hsl(var(--border))]" : ""}
                ${!past && !active ? "text-[hsl(var(--muted-foreground))]" : ""}`}
            >
              {active && <Loader2 className="h-3 w-3 animate-spin" />}
              {past && !active && <CheckCircle className="h-3 w-3" />}
              {p}
            </div>
          );
        })}
      </div>
    </div>
  );
}
