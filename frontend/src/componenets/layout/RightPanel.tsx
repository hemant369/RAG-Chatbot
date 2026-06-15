import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { CheckCircle, Database } from "lucide-react";
import { useEffect, useState } from "react";
import { listDocuments } from "../../api/client";

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

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const docs = await listDocuments();
        const totalChunks = docs.reduce((sum: number, doc: any) => sum + (doc.chunk_count || 0), 0);
        setDocuments({ count: docs.length, chunks: totalChunks });
      } catch (e) {
        console.error("Failed to fetch documents:", e);
      }
    };

    fetchDocuments();
    const interval = setInterval(fetchDocuments, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-5 space-y-5">
      {/* System Status */}
      <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/20 backdrop-blur-xl p-5 shadow-lg rounded-xl">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <h3 className="text-sm font-bold text-white tracking-wide">SYSTEM STATUS</h3>
          </div>

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
      <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/20 backdrop-blur-xl p-5 shadow-lg rounded-xl">
        <h3 className="text-sm font-bold text-white mb-4 tracking-wide">KNOWLEDGE BASE</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
            <span className="text-sm text-slate-300 font-medium">Documents</span>
            <Badge variant="secondary" className="bg-gradient-to-r from-purple-500 to-blue-500 text-white border-0 font-bold px-3">
              {documents.count}
            </Badge>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
            <span className="text-sm text-slate-300 font-medium">Chunks Indexed</span>
            <Badge variant="secondary" className="bg-gradient-to-r from-purple-500 to-blue-500 text-white border-0 font-bold px-3">
              {documents.chunks}
            </Badge>
          </div>
        </div>
      </Card>
    </div>
  );
}

function StatusItem({ icon, label, status, healthy }: any) {
  return (
    <div className="flex items-center justify-between gap-3 p-2 rounded-lg hover:bg-white/5 transition-all">
      <div className="flex min-w-0 items-center gap-3">
        <div className={`flex-shrink-0 ${healthy ? "text-green-400" : "text-red-400"}`}>
          {icon}
        </div>
        <span className="text-sm text-slate-200 leading-snug font-medium">{label}</span>
      </div>
      <span className={`text-xs font-bold flex-shrink-0 px-2 py-1 rounded ${
        healthy
          ? "bg-green-500/20 text-green-300"
          : "bg-red-500/20 text-red-300"
      }`}>
        {status}
      </span>
    </div>
  );
}
