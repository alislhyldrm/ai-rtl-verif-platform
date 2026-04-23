import { useRef, useState } from "react";
import { FileCode } from "lucide-react";
import { uploadRtl } from "@/api/client";
import type { RtlInterface } from "@/api/types";

interface Props {
  onUploaded: (iface: RtlInterface, filename: string) => void;
}

export function RtlUploader({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    if (!file.name.endsWith(".sv")) {
      setError("Only .sv files accepted");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const iface = await uploadRtl(file);
      onUploaded(iface, file.name);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="border-2 border-dashed border-[hsl(var(--border))] rounded-lg p-8 text-center
                 hover:border-[hsl(var(--muted-foreground))] transition-colors cursor-pointer"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".sv"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
      <FileCode className="mx-auto h-8 w-8 text-[hsl(var(--muted-foreground))] mb-3" />
      <p className="text-sm text-[hsl(var(--muted-foreground))] mb-2">
        Drag & drop a <span className="font-mono text-[hsl(var(--foreground))]">.sv</span> file, or{" "}
        <span className="text-[hsl(var(--primary))] underline">browse</span>
      </p>
      {loading && <p className="text-xs text-[hsl(var(--muted-foreground))] mt-2">Parsing RTL…</p>}
      {error && <p className="text-xs text-red-400 mt-2">{error}</p>}
    </div>
  );
}
