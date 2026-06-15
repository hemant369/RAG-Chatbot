import { MessageCircle, Upload, Library, Settings, Zap } from "lucide-react";
import { Button } from "../ui/button";
import clsx from "clsx";
import { useEffect, useState } from "react";

const navItems = [
  { id: "chat", label: "Chat", icon: MessageCircle },
  { id: "upload", label: "Upload Docs", icon: Upload },
  { id: "library", label: "Library", icon: Library },
  { id: "settings", label: "Settings", icon: Settings }
];

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        const data = await res.json();
        setBackendOnline(res.ok && data.status === "healthy");
      } catch {
        setBackendOnline(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
          <Zap className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">RAG</h1>
          <p className="text-xs text-slate-400">Assistant</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <Button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              variant={isActive ? "default" : "ghost"}
              className={clsx(
                "w-full justify-start gap-3 h-10",
                isActive
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  : "text-slate-300 hover:text-white hover:bg-white/10"
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Button>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="flex-1 border-t border-white/10" />

      {/* Status Badge */}
      <div className="px-3 py-2 rounded-lg bg-white/5 border border-white/10">
        <div className="flex items-center gap-2 mb-2">
          <div
            className={clsx(
              "w-2 h-2 rounded-full",
              backendOnline ? "bg-green-500 animate-pulse" : "bg-red-500"
            )}
          />
          <span className="text-xs font-medium text-slate-300">
            {backendOnline ? "Connected" : "Disconnected"}
          </span>
        </div>
        <p className="text-xs text-slate-400">
          {backendOnline ? "Backend online" : "Backend offline"}
        </p>
      </div>
    </div>
  );
}
