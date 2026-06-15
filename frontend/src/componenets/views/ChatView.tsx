import { useState, useEffect, useRef } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Bot, Send, Loader2, Trash2, User, Paperclip, X } from "lucide-react";
import { clearChat, sendChat, uploadDocument } from "../../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  reasoning?: any;
}

export function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((m) => [...m, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendChat(input, messages);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: response.answer || "No response",
          reasoning: response.agent_reasoning,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Error: Failed to get response" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleClearChat() {
    try {
      await clearChat();
    } catch (e) {
      console.error("Failed to clear backend chat history:", e);
    } finally {
      setMessages([]);
    }
  }

  async function handleFileUpload(file: File) {
    setUploading(true);
    try {
      await uploadDocument(file);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `✅ Successfully uploaded "${file.name}". The document has been indexed and is ready for questions!`,
        },
      ]);
      setUploadedFile(null);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `❌ Failed to upload "${file.name}". Please try again.`,
        },
      ]);
    } finally {
      setUploading(false);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  }

  function removeFile() {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <div className="flex h-full flex-col gap-6 p-8 bg-gradient-to-br from-slate-50 to-white">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
            Chat
          </h1>
          <p className="text-sm text-slate-600 mt-1">Ask questions about your documents</p>
        </div>
        <Button
          onClick={handleClearChat}
          variant="ghost"
          className="gap-2 border border-slate-200 bg-white text-slate-600 shadow-sm hover:bg-slate-50 hover:text-slate-950 hover:border-slate-300 transition-all"
        >
          <Trash2 className="h-4 w-4" />
          Clear
        </Button>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden border-slate-200 bg-white p-6 shadow-lg rounded-2xl">
        <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center space-y-4 max-w-md">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 shadow-lg">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-slate-800">Welcome to RAG Assistant</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  Start a conversation by asking questions about your uploaded documents.
                  I'll help you find answers using AI-powered search.
                </p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {loading && (
            <div className="flex items-start gap-4 animate-fadeIn">
              <div className="mt-1 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 shadow-sm">
                <Bot className="h-5 w-5 text-slate-600" />
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 shadow-md">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
                  <span className="text-sm text-slate-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>

      <div className="space-y-3">
        {/* File Preview */}
        {uploadedFile && (
          <div className="flex items-center gap-3 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-xl px-4 py-3 shadow-md animate-fadeIn">
            <div className="p-2 rounded-lg bg-white shadow-sm">
              <Paperclip className="h-4 w-4 text-purple-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-purple-900 truncate">{uploadedFile.name}</p>
              <p className="text-xs text-purple-600">Ready to upload</p>
            </div>
            <Button
              onClick={removeFile}
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-purple-600 hover:text-purple-800 hover:bg-purple-100 rounded-lg"
            >
              <X className="h-4 w-4" />
            </Button>
            <Button
              onClick={() => handleFileUpload(uploadedFile)}
              disabled={uploading}
              className="h-8 px-4 text-xs font-medium rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-md hover:shadow-lg transition-all"
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Uploading...
                </span>
              ) : (
                "Upload Now"
              )}
            </Button>
          </div>
        )}

        {/* Input Area */}
        <div className="flex gap-2 items-center bg-white p-3 rounded-2xl border-2 border-slate-200 shadow-lg hover:border-purple-300 transition-colors">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".pdf,.txt,.md,.json,.yaml,.yml,.csv"
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="ghost"
            className="h-10 w-10 p-0 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center"
            aria-label="Attach file"
            title="Upload document"
          >
            <Paperclip className="h-5 w-5" />
          </Button>
          <div className="w-px h-8 bg-slate-200" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Type your question or upload a document..."
            className="flex-1 bg-transparent px-3 py-2 text-slate-950 placeholder:text-slate-400 focus:outline-none"
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="h-11 w-11 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md hover:from-purple-700 hover:to-blue-700 hover:shadow-lg disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400 transition-all flex items-center justify-center"
            aria-label="Send message"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </Button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 ${isUser ? "flex-row-reverse" : "flex-row"} animate-fadeIn`}>
      <div
        className={`mt-1 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl shadow-md ${
          isUser
            ? "bg-gradient-to-br from-slate-900 to-slate-700 text-white"
            : "bg-gradient-to-br from-slate-100 to-slate-200 text-slate-700"
        }`}
      >
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>
      <div
        className={`max-w-[70%] rounded-2xl px-5 py-4 shadow-md transition-all hover:shadow-lg ${
          isUser
            ? "bg-gradient-to-br from-slate-900 to-slate-800 text-white"
            : "border border-slate-200 bg-white text-slate-800"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        {message.reasoning?.thought && (
          <details className={`mt-3 text-xs ${isUser ? "text-slate-400" : "text-slate-500"}`}>
            <summary className="cursor-pointer hover:text-purple-600 transition font-medium">
              View Reasoning
            </summary>
            <pre className="mt-2 overflow-auto text-xs bg-slate-50 p-3 rounded-lg border border-slate-200">{message.reasoning.thought}</pre>
          </details>
        )}
      </div>
    </div>
  );
}
