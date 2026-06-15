import { useState } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import { uploadDocument } from "../../api/client";

export function UploadView() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    try {
      await uploadDocument(file);
      setStatus("success");
      setMessage("Document uploaded successfully!");
      setFile(null);
      setTimeout(() => setStatus("idle"), 3000);
    } catch (e) {
      setStatus("error");
      setMessage("Failed to upload document");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full p-6 gap-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Upload Documents</h1>
        <p className="text-sm text-slate-500">Add files to your knowledge base</p>
      </div>

      <Card className="bg-white border-slate-200 shadow-sm p-8 flex-1 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 mx-auto flex items-center justify-center">
            <Upload className="w-8 h-8 text-white" />
          </div>

          <div>
            <h2 className="text-lg font-semibold text-slate-950">Upload Documents</h2>
            <p className="text-sm text-slate-500 mt-1">PDF, TXT, MD, JSON, YAML</p>
          </div>

          <label className="flex flex-col gap-2">
            <div className="px-4 py-3 rounded-lg border-2 border-dashed border-slate-300 hover:border-slate-400 transition cursor-pointer bg-slate-50 hover:bg-slate-100">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                accept=".pdf,.txt,.md,.json,.yaml,.yml,.csv"
              />
              <p className="text-sm text-slate-700">
                {file ? file.name : "Click to select or drag & drop"}
              </p>
            </div>
          </label>

          {file && (
            <Button 
              onClick={handleUpload} 
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              {loading ? "Uploading..." : "Upload Document"}
            </Button>
          )}

          {status === "success" && (
            <div className="flex gap-2 items-center text-green-400 text-sm">
              <CheckCircle className="w-4 h-4" />
              {message}
            </div>
          )}
          {status === "error" && (
            <div className="flex gap-2 items-center text-red-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              {message}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
