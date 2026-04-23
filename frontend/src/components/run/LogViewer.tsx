import LazyLog from "@melloware/react-logviewer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  lines: string[];
}

export function LogViewer({ lines }: Props) {
  const text = lines.length > 0 ? lines.join("\n") : " ";
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Simulator Output</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-64 rounded-b-lg overflow-hidden">
          <LazyLog
            text={text}
            follow
            enableSearch={false}
            style={{ fontFamily: "monospace", fontSize: 12 }}
          />
        </div>
      </CardContent>
    </Card>
  );
}
