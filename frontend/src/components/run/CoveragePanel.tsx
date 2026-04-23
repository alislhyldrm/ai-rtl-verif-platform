import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Area, AreaChart, XAxis, YAxis } from "recharts";
import type { CoverageGap } from "@/api/types";

interface Props {
  pct: number;
  target: number;
  history: number[];
  gaps: CoverageGap[];
}

export function CoveragePanel({ pct, target, history, gaps }: Props) {
  const chartData = history.map((v, i) => ({ iter: i + 1, pct: v }));
  const done = pct >= target;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex justify-between items-baseline">
          <span>Coverage</span>
          <span className={done ? "text-green-400" : "text-yellow-400"}>
            {pct.toFixed(1)}% / {target}%
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={Math.min((pct / target) * 100, 100)} className="h-2" />

        {chartData.length >= 2 && (
          <ChartContainer
            config={{ pct: { label: "Coverage", color: "hsl(var(--primary))" } }}
            className="h-24"
          >
            <AreaChart data={chartData}>
              <XAxis dataKey="iter" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="pct"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary) / 0.2)"
              />
            </AreaChart>
          </ChartContainer>
        )}

        {gaps.length > 0 && (
          <div>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-2">
              UNCOVERED ({gaps.length})
            </p>
            <ul className="space-y-1 max-h-32 overflow-auto">
              {gaps.map((g, i) => (
                <li key={i} className="text-xs font-mono text-[hsl(var(--muted-foreground))]">
                  <span className="text-[hsl(var(--foreground))]">{g.file}:{g.line}</span>{" "}
                  [{g.type}] {g.description}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
