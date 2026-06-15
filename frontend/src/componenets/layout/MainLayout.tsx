import React from "react";
import { Sidebar } from "./Sidebar";
import { RightPanel } from "./RightPanel";
import { BackendLogsPanel } from "../panels/BackendLogsPanel";

interface MainLayoutProps {
  activeView: string;
  onViewChange: (view: any) => void;
  children: React.ReactNode;
}

export function MainLayout({ activeView, onViewChange, children }: MainLayoutProps) {
  return (
    <div className="h-screen bg-white flex overflow-hidden">
      {/* Left Sidebar */}
      <div className="w-80 bg-black border-r border-slate-800 flex flex-col">
        <Sidebar activeView={activeView} onViewChange={onViewChange} />
        <div className="flex-1 overflow-auto border-t border-white/10">
          <RightPanel />
        </div>
      </div>

      {/* Center Content */}
      <main className="flex-1 flex flex-col overflow-hidden bg-white">
        {children}
      </main>

      {/* Right Panel */}
      <div className="w-96 h-full bg-white border-l border-slate-200 overflow-hidden p-6 flex flex-col">
        <BackendLogsPanel />
      </div>
    </div>
  );
}
