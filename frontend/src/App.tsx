import { useState } from "react";
import { MainLayout } from "./componenets/layout/MainLayout";
import { ChatView } from "./componenets/views/ChatView";
import { LibraryView } from "./componenets/views/LibraryView";
import { SettingsView } from "./componenets/views/SettingsView";

export default function App() {
  const [activeView, setActiveView] = useState<"chat" | "library" | "settings">("chat");

  return (
    <MainLayout activeView={activeView} onViewChange={setActiveView}>
      {activeView === "chat" && <ChatView />}
      {activeView === "library" && <LibraryView />}
      {activeView === "settings" && <SettingsView />}
    </MainLayout>
  );
}