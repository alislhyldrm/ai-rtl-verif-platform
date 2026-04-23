import { useEffect, useState } from "react";
import Editor from "@monaco-editor/react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTestCode } from "@/api/client";

interface Props {
  runId: string;
  testUrls: Map<number, string>;
}

export function TestCodeViewer({ runId, testUrls }: Props) {
  const iterations = Array.from(testUrls.keys()).sort((a, b) => a - b);
  const [codes, setCodes] = useState<Map<number, string>>(new Map());

  useEffect(() => {
    for (const iter of iterations) {
      if (!codes.has(iter)) {
        getTestCode(runId, iter).then(({ code }) =>
          setCodes((prev) => new Map(prev).set(iter, code))
        );
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iterations.length]);

  if (iterations.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Generated Tests</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue={String(iterations[0])}>
          <TabsList className="w-full justify-start rounded-none border-b px-4">
            {iterations.map((i) => (
              <TabsTrigger key={i} value={String(i)} className="text-xs">
                iter {i}
              </TabsTrigger>
            ))}
          </TabsList>
          {iterations.map((i) => (
            <TabsContent key={i} value={String(i)} className="m-0">
              <Editor
                height="320px"
                language="python"
                theme="vs-dark"
                value={codes.get(i) ?? "# Loading…"}
                options={{ readOnly: true, minimap: { enabled: false }, fontSize: 12 }}
              />
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  );
}
