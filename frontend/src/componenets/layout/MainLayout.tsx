import React from "react";
import { Sidebar } from "./Sidebar";
import { BackendLogsPanel } from "../panels/BackendLogsPanel";

interface MainLayoutProps {
  activeView: string;
  onViewChange: (view: any) => void;
  children: React.ReactNode;
}

export function MainLayout({ activeView, onViewChange, children }: MainLayoutProps) {
  return (
    <div className="h-screen bg-slate-100 flex overflow-hidden">
      {/* Left Sidebar */}
      <div className="w-80 bg-black flex flex-col shadow-xl relative">
        <Sidebar activeView={activeView} onViewChange={onViewChange} />
        <div className="flex-1 overflow-auto border-t border-white/10">
          <BackendLogsPanel />
        </div>
        {/* Right border separator */}
        <div className="absolute right-0 top-0 bottom-0 w-px bg-gradient-to-b from-slate-700 via-slate-600 to-slate-700" />
      </div>

      {/* Center Content - Now takes full remaining width */}
      <main className="flex-1 flex flex-col overflow-hidden bg-white shadow-inner">
        {children}
      </main>
    </div>
  );
}
