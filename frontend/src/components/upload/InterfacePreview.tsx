import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { RtlInterface } from "@/api/types";

export function InterfacePreview({ iface }: { iface: RtlInterface }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-mono">
          module <span className="text-blue-400">{iface.module}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mb-2">PORTS</p>
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-[hsl(var(--muted-foreground))] border-b border-[hsl(var(--border))]">
                <th className="text-left pb-1">name</th>
                <th className="text-left pb-1">dir</th>
                <th className="text-left pb-1">width</th>
              </tr>
            </thead>
            <tbody>
              {iface.ports.map((p) => (
                <tr key={p.name} className="border-b border-[hsl(var(--border))]/50">
                  <td className="py-1">{p.name}</td>
                  <td className="py-1">
                    <Badge variant={p.direction === "input" ? "secondary" : "outline"}>
                      {p.direction}
                    </Badge>
                  </td>
                  <td className="py-1">{p.width}b</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {iface.fsm_states.length > 0 && (
          <div>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-2">FSM STATES</p>
            <div className="flex flex-wrap gap-1">
              {iface.fsm_states.map((s) => (
                <Badge key={s} variant="outline" className="font-mono text-xs">
                  {s}
                </Badge>
              ))}
            </div>
          </div>
        )}
        {iface.reset && (
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            Reset: <span className="text-[hsl(var(--foreground))] font-mono">{iface.reset.signal}</span>{" "}
            (active {iface.reset.active})
          </p>
        )}
      </CardContent>
    </Card>
  );
}
