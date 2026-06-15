import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

export async function sendChat(query, chatHistory = []) {
  const payload = {
    query,
    chat_history: chatHistory
  };
  const response = await api.post("/chat/message", payload);
  return response.data;
}

export async function clearChat() {
  const response = await api.post("/chat/clear");
  return response.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data;
}

export async function listDocuments() {
  const response = await api.get("/documents/list");
  return response.data.documents || [];
}

export async function deleteDocument(id) {
  const response = await api.delete(`/documents/${id}`);
  return response.data;
}

/* Open server-sent events stream for logs (falls back to null if not supported) */
export function openLogsStream(onLine, onError) {
  try {
    const url = `${BASE_URL.replace(/\/$/, "")}/logs/stream`;
    if (typeof EventSource === "undefined") {
      onError?.(new Error("EventSource not supported in this environment"));
      return null;
    }
    const es = new EventSource(url);
    es.onmessage = (ev) => onLine(ev.data);
    es.onerror = (e) => {
      es.close();
      onError?.(e);
    };
    return es;
  } catch (e) {
    onError?.(e);
    return null;
  }
}
