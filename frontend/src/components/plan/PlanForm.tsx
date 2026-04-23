import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Play } from "lucide-react";
import type { RtlInterface, VerificationPlan } from "@/api/types";

interface Props {
  iface: RtlInterface;
  rtlFilename: string;
  onSubmit: (plan: VerificationPlan) => void;
}

export function PlanForm({ iface, rtlFilename, onSubmit }: Props) {
  const [baudDivs, setBaudDivs] = useState("10, 20, 50");
  const [testData, setTestData] = useState("0x00, 0xFF, 0xA5");
  const [targetPct, setTargetPct] = useState("90");
  const [maxIter, setMaxIter] = useState("5");
  const [protocol, setProtocol] = useState("UART_8N1");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const baud_divs = baudDivs.split(",").map((s) => {
        const n = parseInt(s.trim(), 10);
        if (isNaN(n) || n < 4) throw new Error(`baud_div "${s.trim()}" must be >= 4`);
        return n;
      });
      const test_data = testData.split(",").map((s) => {
        const n = parseInt(s.trim(), 16);
        if (isNaN(n) || n < 0 || n > 255) throw new Error(`"${s.trim()}" is not a valid byte`);
        return n;
      });
      onSubmit({
        module: iface.module,
        rtl_file: rtlFilename,
        protocol: protocol as VerificationPlan["protocol"],
        baud_divs,
        test_data,
        coverage_target_pct: parseInt(targetPct, 10),
        max_iterations: parseInt(maxIter, 10),
      });
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Verification Plan</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="module">Module</Label>
              <Input id="module" value={iface.module} readOnly className="font-mono" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="protocol">Protocol</Label>
              <Select value={protocol} onValueChange={setProtocol}>
                <SelectTrigger id="protocol">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["UART_8N1", "SPI", "I2C", "AXI4L", "CUSTOM"].map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1">
            <Label htmlFor="baud-divs">Baud dividers (comma-separated, min 4)</Label>
            <Input
              id="baud-divs"
              value={baudDivs}
              onChange={(e) => setBaudDivs(e.target.value)}
              className="font-mono"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="test-data">Test data bytes (hex, comma-separated)</Label>
            <Input
              id="test-data"
              value={testData}
              onChange={(e) => setTestData(e.target.value)}
              className="font-mono"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="target">Coverage target (%)</Label>
              <Input
                id="target"
                type="number"
                min={1}
                max={100}
                value={targetPct}
                onChange={(e) => setTargetPct(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="max-iter">Max iterations</Label>
              <Input
                id="max-iter"
                type="number"
                min={1}
                max={10}
                value={maxIter}
                onChange={(e) => setMaxIter(e.target.value)}
              />
            </div>
          </div>
          {error && <p className="text-xs text-red-400">{error}</p>}
          <Button type="submit" className="w-full gap-2">
            <Play className="h-4 w-4" />
            Start Verification Run
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
