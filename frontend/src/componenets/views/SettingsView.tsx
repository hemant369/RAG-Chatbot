import { useEffect, useState } from "react";
import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { Activity, Database, Server, AlertCircle, CheckCircle, Cpu } from "lucide-react";
import { listDocuments } from "../../api/client";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function SettingsView() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [backendInfo, setBackendInfo] = useState<any>(null);
  const [documents, setDocuments] = useState({ count: 0, chunks: 0 });

  useEffect(() => {
    checkBackendHealth();
    fetchDocuments();

    const healthInterval = setInterval(checkBackendHealth, 5000);
    const docsInterval = setInterval(fetchDocuments, 10000);

    return () => {
      clearInterval(healthInterval);
      clearInterval(docsInterval);
    };
  }, []);

  async function checkBackendHealth() {
    setBackendStatus("checking");
    try {
      const response = await fetch(`${BASE_URL}/health`);
      if (response.ok) {
        setBackendStatus("online");
        const info = await fetch(`${BASE_URL}/`).then(r => r.json());
        setBackendInfo(info);
      } else {
        setBackendStatus("offline");
      }
    } catch (e) {
      setBackendStatus("offline");
    }
  }

  async function fetchDocuments() {
    try {
      const docs = await listDocuments();
      const totalChunks = docs.reduce((sum: number, doc: any) => sum + (doc.chunk_count || 0), 0);
      setDocuments({ count: docs.length, chunks: totalChunks });
    } catch (e) {
      console.error("Failed to fetch documents:", e);
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-white p-4">
      <div className="mb-3">
        <h1 className="text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
          System Info
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">Monitor system status</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 auto-rows-fr">
        {/* System Status */}
        <Card className="bg-white border-slate-200 shadow-sm rounded-lg p-3 flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 rounded-md bg-gradient-to-br from-green-50 to-emerald-50">
              <CheckCircle className="w-4 h-4 text-green-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-950">System Status</h2>
              <p className="text-xs text-slate-500">Backend components</p>
            </div>
          </div>

          <div className="space-y-1.5">
            <StatusItem
              label="Ollama/Qwen 2.5 3B"
              status={backendStatus === "online" ? "Connected" : "Offline"}
              healthy={backendStatus === "online"}
            />
            <StatusItem
              label="ChromaDB"
              status={backendStatus === "online" ? "Connected" : "Offline"}
              healthy={backendStatus === "online"}
            />
            <StatusItem
              label="Retriever"
              status={backendStatus === "online" ? "Ready" : "Offline"}
              healthy={backendStatus === "online"}
            />
          </div>
        </Card>

        {/* Knowledge Base Stats */}
        <Card className="bg-white border-slate-200 shadow-sm rounded-lg p-3 flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 rounded-md bg-gradient-to-br from-purple-50 to-blue-50">
              <Database className="w-4 h-4 text-purple-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-950">Knowledge Base</h2>
              <p className="text-xs text-slate-500">Indexed documents</p>
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between p-2 rounded-md bg-gradient-to-br from-slate-50 to-white border border-slate-200">
              <span className="text-xs font-medium text-slate-700">Documents</span>
              <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0 text-xs px-2 py-0.5">
                {documents.count}
              </Badge>
            </div>
            <div className="flex items-center justify-between p-2 rounded-md bg-gradient-to-br from-slate-50 to-white border border-slate-200">
              <span className="text-xs font-medium text-slate-700">Chunks Indexed</span>
              <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0 text-xs px-2 py-0.5">
                {documents.chunks}
              </Badge>
            </div>
          </div>
        </Card>

        {/* Backend Connection */}
        <Card className="bg-white border-slate-200 shadow-sm rounded-lg p-3 flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 rounded-md bg-gradient-to-br from-blue-50 to-cyan-50">
              <Server className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-950">Backend Connection</h2>
              <p className="text-xs text-slate-500">API server details</p>
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-xs font-medium text-slate-600">Status</span>
              <div className="flex items-center gap-2">
                {backendStatus === "checking" && (
                  <Badge variant="outline" className="gap-1 text-xs px-2 py-0.5">
                    <Activity className="w-3 h-3 animate-pulse" />
                    Checking...
                  </Badge>
                )}
                {backendStatus === "online" && (
                  <Badge className="gap-1 bg-green-100 text-green-700 hover:bg-green-100 text-xs px-2 py-0.5">
                    <CheckCircle className="w-3 h-3" />
                    Online
                  </Badge>
                )}
                {backendStatus === "offline" && (
                  <Badge variant="destructive" className="gap-1 text-xs px-2 py-0.5">
                    <AlertCircle className="w-3 h-3" />
                    Offline
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-xs font-medium text-slate-600">API URL</span>
              <span className="text-xs font-mono text-slate-900 truncate max-w-[200px]">{BASE_URL}</span>
            </div>

            {backendInfo && (
              <>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
                  <span className="text-xs font-medium text-slate-600">API Version</span>
                  <span className="text-xs font-mono text-slate-900">{backendInfo.version}</span>
                </div>
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-xs font-medium text-slate-600">API Name</span>
                  <span className="text-xs font-mono text-slate-900">{backendInfo.message}</span>
                </div>
              </>
            )}
          </div>

          <button
            onClick={checkBackendHealth}
            className="mt-2 w-full px-3 py-1.5 text-xs font-medium rounded-md bg-gradient-to-r from-blue-600 to-cyan-600 text-white hover:from-blue-700 hover:to-cyan-700 transition-all"
          >
            Refresh
          </button>
        </Card>

        {/* Frontend Information */}
        <Card className="bg-white border-slate-200 shadow-sm rounded-lg p-3 flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 rounded-md bg-gradient-to-br from-orange-50 to-amber-50">
              <Cpu className="w-4 h-4 text-orange-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-950">Frontend Stack</h2>
              <p className="text-xs text-slate-500">Client configuration</p>
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-xs font-medium text-slate-600">Framework</span>
              <span className="text-xs font-mono text-slate-900">React + TS</span>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-xs font-medium text-slate-600">Build Tool</span>
              <span className="text-xs font-mono text-slate-900">Vite</span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-xs font-medium text-slate-600">UI Library</span>
              <span className="text-xs font-mono text-slate-900">Tailwind CSS</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatusItem({ label, status, healthy }: { label: string; status: string; healthy: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-slate-100 last:border-0">
      <div className="flex items-center gap-1.5">
        <div className={`w-1.5 h-1.5 rounded-full ${healthy ? "bg-green-500" : "bg-red-500"}`} />
        <span className="text-xs font-medium text-slate-700">{label}</span>
      </div>
      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
        healthy ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}>
        {status}
      </span>
    </div>
  );
}
