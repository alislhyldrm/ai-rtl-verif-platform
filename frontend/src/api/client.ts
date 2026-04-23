import type {
  RtlInterface,
  VerificationPlan,
  RunResponse,
  RunReport,
  TestCodeResponse,
} from "./types";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadRtl(file: File): Promise<RtlInterface> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/upload-rtl", { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function validatePlan(
  plan: VerificationPlan
): Promise<{ valid: boolean; errors?: unknown[] }> {
  return post("/api/validate-plan", plan);
}

export async function startRun(plan: VerificationPlan): Promise<RunResponse> {
  return post("/api/run", plan);
}

export async function getReport(runId: string): Promise<RunReport> {
  const res = await fetch(`/api/runs/${runId}/report`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getTestCode(
  runId: string,
  iteration: number
): Promise<TestCodeResponse> {
  const res = await fetch(`/api/runs/${runId}/tests/${iteration}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function cancelRun(runId: string): Promise<void> {
  await fetch(`/api/runs/${runId}`, { method: "DELETE" });
}
