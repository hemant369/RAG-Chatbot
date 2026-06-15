import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { CheckCircle, Database } from "lucide-react";
import { useEffect, useState } from "react";

export function RightPanel() {
  const [health, setHealth] = useState<any>(null);
  const [documents, setDocuments] = useState({ count: 0, chunks: 0 });
  const backendOnline = health?.status === "healthy";

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        setHealth(await res.json());
      } catch (e) {
        setHealth({ status: "unavailable" });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 space-y-4">
      {/* System Status */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white">System Status</h3>
          
          <StatusItem 
            icon={<CheckCircle className="w-4 h-4" />}
            label="Ollama/Qwen 2.5 3B"
            status={backendOnline ? "Connected" : "Offline"}
            healthy={backendOnline}
          />
          <StatusItem 
            icon={<Database className="w-4 h-4" />}
            label="ChromaDB" 
            status={backendOnline ? "Connected" : "Offline"}
            healthy={backendOnline}
          />
          <StatusItem 
            icon={<CheckCircle className="w-4 h-4" />}
            label="Retriever" 
            status={backendOnline ? "Ready" : "Offline"}
            healthy={backendOnline}
          />
        </div>
      </Card>

      {/* Documents Stats */}
      <Card className="bg-white/5 border-white/10 p-4">
        <h3 className="text-sm font-semibold text-white mb-3">Knowledge Base</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Documents</span>
            <Badge variant="secondary">{documents.count}</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Chunks Indexed</span>
            <Badge variant="secondary">{documents.chunks}</Badge>
          </div>
        </div>
      </Card>
    </div>
  );
}

function StatusItem({ icon, label, status, healthy }: any) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="flex min-w-0 items-center gap-2">
        <div className={healthy ? "text-green-400 flex-shrink-0" : "text-red-400 flex-shrink-0"}>
          {icon}
        </div>
        <span className="text-sm text-slate-300 leading-snug">{label}</span>
      </div>
      <span className={`text-xs font-medium flex-shrink-0 ${healthy ? "text-green-400" : "text-red-400"}`}>
        {status}
      </span>
    </div>
  );
}
