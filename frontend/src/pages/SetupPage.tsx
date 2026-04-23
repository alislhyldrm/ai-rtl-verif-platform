import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { RtlUploader } from "@/components/upload/RtlUploader";
import { InterfacePreview } from "@/components/upload/InterfacePreview";
import { PlanForm } from "@/components/plan/PlanForm";
import { startRun } from "@/api/client";
import type { RtlInterface, VerificationPlan } from "@/api/types";

export function SetupPage() {
  const [iface, setIface] = useState<RtlInterface | null>(null);
  const [filename, setFilename] = useState("");
  const [starting, setStarting] = useState(false);
  const navigate = useNavigate();

  async function handleStart(plan: VerificationPlan) {
    setStarting(true);
    try {
      const { run_id } = await startRun(plan);
      navigate(`/run/${run_id}`);
    } catch (e) {
      alert(String(e));
      setStarting(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold">Verification Setup</h1>
      {!iface ? (
        <RtlUploader onUploaded={(i, f) => { setIface(i); setFilename(f); }} />
      ) : (
        <div className="space-y-4">
          <InterfacePreview iface={iface} />
          <PlanForm iface={iface} rtlFilename={filename} onSubmit={handleStart} />
          {starting && (
            <p className="text-xs text-[hsl(var(--muted-foreground))] text-center">
              Starting run…
            </p>
          )}
        </div>
      )}
    </div>
  );
}
