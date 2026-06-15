import { useEffect, useRef, useState } from "react";

export function BackendLogsPanel() {
  const [logs, setLogs] = useState<string[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const apiBaseUrl = (import.meta as any).env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

    const stopPolling = () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };

    const loadSnapshot = async () => {
      const res = await fetch(`${apiBaseUrl}/logs`);
      const data = await res.json();
      setLogs((data.logs || []).map(formatLogMessage));
    };

    const startPolling = () => {
      if (pollingRef.current) return;
      loadSnapshot().catch((e) => console.error("Logs polling error:", e));
      pollingRef.current = setInterval(() => {
        loadSnapshot().catch((e) => console.error("Logs polling error:", e));
      }, 2000);
    };

    try {
      const es = new EventSource(`${apiBaseUrl}/logs/stream`);
      es.onopen = () => {
        stopPolling();
      };
      es.onmessage = (e) => {
        setLogs((prev) => [...prev.slice(-99), formatLogMessage(e.data)]);
      };
      es.onerror = () => {
        es.close();
        startPolling();
      };
      return () => {
        es.close();
        stopPolling();
      };
    } catch {
      startPolling();
      return stopPolling;
    }
  }, []);

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight });
  }, [logs]);

  return (
    <div className="h-full min-h-0 bg-black rounded-lg border border-slate-800 shadow-sm flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950">
        <div>
          <h3 className="text-sm font-semibold text-green-400">Backend Logs</h3>
          <p className="text-xs text-green-400/70">Live runtime messages</p>
        </div>
        <button
          onClick={() => setLogs([])}
          className="text-xs px-2 py-1 rounded border border-green-900/60 text-green-400 hover:bg-green-950 hover:text-green-200 transition"
        >
          Clear
        </button>
      </div>
      <div
        ref={containerRef}
        className="logs-scroll flex-1 min-h-0 overflow-y-auto text-xs font-mono text-green-500 p-4 space-y-1"
      >
        {logs.length === 0 && <div className="text-green-900">Waiting for logs...</div>}
        {logs.map((log, i) => (
          <div
            key={i}
            className="flex gap-2 break-words rounded border border-slate-800/60 px-2 py-1 text-green-500 hover:bg-green-950/40 hover:text-green-300 transition"
          >
            <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-green-500" />
            <span className="min-w-0 flex-1">{log}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


function formatLogMessage(line: string) {
  const parts = line.split(" | ");
  return parts[parts.length - 1] || line;
}
