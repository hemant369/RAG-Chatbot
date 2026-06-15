import { useState } from "react";
import { MainLayout } from "./componenets/layout/MainLayout";
import { ChatView } from "./componenets/views/ChatView";
import { UploadView } from "./componenets/views/UploadView";
import { LibraryView } from "./componenets/views/LibraryView";
import { SettingsView } from "./componenets/views/SettingsView";

export default function App() {
  const [activeView, setActiveView] = useState<"chat" | "upload" | "library" | "settings">("chat");

  return (
    <MainLayout activeView={activeView} onViewChange={setActiveView}>
      {activeView === "chat" && <ChatView />}
      {activeView === "upload" && <UploadView />}
      {activeView === "library" && <LibraryView />}
      {activeView === "settings" && <SettingsView />}
    </MainLayout>
  );
}