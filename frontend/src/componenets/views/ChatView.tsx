import { useState, useEffect, useRef } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Bot, Send, Loader2, Trash2, User } from "lucide-react";
import { clearChat, sendChat } from "../../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  reasoning?: any;
}

export function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

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

  return (
    <div className="flex h-full flex-col gap-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-950">Chat</h1>
          <p className="text-sm text-slate-500">Ask questions about your documents</p>
        </div>
        <Button
          onClick={handleClearChat}
          variant="ghost"
          className="gap-2 border border-slate-200 bg-white text-slate-600 shadow-sm hover:bg-slate-50 hover:text-slate-950"
        >
          <Trash2 className="h-4 w-4" />
          Clear
        </Button>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden border-slate-200 bg-white p-4 shadow-sm">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pr-2">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
                  <Bot className="h-5 w-5 text-slate-500" />
                </div>
                <p className="text-slate-500">Start a conversation...</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {loading && (
            <div className="flex items-start gap-3">
              <div className="mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-100">
                <Bot className="h-4 w-4 text-slate-600" />
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
                <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
              </div>
            </div>
          )}
        </div>
      </Card>

      <div className="flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your question..."
          className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-950 placeholder:text-slate-400 transition focus:border-slate-950 focus:outline-none focus:ring-2 focus:ring-slate-100"
        />
        <Button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="h-12 w-12 rounded-lg bg-slate-950 text-white shadow-sm hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-400"
          aria-label="Send message"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div
        className={`mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${
          isUser
            ? "bg-slate-950 text-white"
            : "border border-slate-200 bg-slate-100 text-slate-600"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 shadow-sm ${
          isUser
            ? "bg-slate-950 text-white"
            : "border border-slate-200 bg-slate-50 text-slate-800"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        {message.reasoning?.thought && (
          <details className="mt-2 text-xs text-slate-400">
            <summary className="cursor-pointer">Reasoning</summary>
            <pre className="mt-1 overflow-auto text-xs">{message.reasoning.thought}</pre>
          </details>
        )}
      </div>
    </div>
  );
}
