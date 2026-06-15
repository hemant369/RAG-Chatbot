import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { CheckCircle, AlertCircle, Database } from "lucide-react";
import { useEffect, useState } from "react";

export function RightPanel() {
  const [health, setHealth] = useState<any>(null);
  const [documents, setDocuments] = useState({ count: 0, chunks: 0 });

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
    <div className="p-6 space-y-6">
      {/* System Status */}
      <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/20 backdrop-blur-xl p-4">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white">System Status</h3>
          
          <StatusItem 
            icon={<CheckCircle className="w-4 h-4" />}
            label="Ollama" 
            status={health?.status === "healthy" ? "Connected" : "Offline"}
            healthy={health?.status === "healthy"}
          />
          <StatusItem 
            icon={<Database className="w-4 h-4" />}
            label="ChromaDB" 
            status="Connected"
            healthy={true}
          />
          <StatusItem 
            icon={<CheckCircle className="w-4 h-4" />}
            label="Retriever" 
            status="Ready"
            healthy={true}
          />
        </div>
      </Card>

      {/* Documents Stats */}
      <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/20 backdrop-blur-xl p-4">
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

      {/* Model Info */}
      <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/20 backdrop-blur-xl p-4">
        <h3 className="text-sm font-semibold text-white mb-2">Model</h3>
        <p className="text-xs text-slate-400">Qwen 2.5 3B</p>
        <p className="text-xs text-slate-500 mt-1">Local inference</p>
      </Card>
    </div>
  );
}

function StatusItem({ icon, label, status, healthy }: any) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className={healthy ? "text-green-400" : "text-red-400"}>
          {icon}
        </div>
        <span className="text-sm text-slate-300">{label}</span>
      </div>
      <span className={`text-xs font-medium ${healthy ? "text-green-400" : "text-red-400"}`}>
        {status}
      </span>
    </div>
  );
}