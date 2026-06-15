import { useState } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import { uploadDocument } from "../../api/client";
import { useApiCall } from "../../hooks/useApiCall";

export function UploadView() {
  const [file, setFile] = useState<File | null>(null);

  const uploadApi = useApiCall({
    onSuccess: () => {
      setFile(null);
    },
  });

  async function handleUpload() {
    if (!file) return;
    await uploadApi.execute(() => uploadDocument(file));
  }

  return (
    <div className="flex flex-col h-full p-8 gap-6 bg-gradient-to-br from-slate-50 to-white">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
          Upload Documents
        </h1>
        <p className="text-sm text-slate-600 mt-1">Add files to your knowledge base for AI-powered search</p>
      </div>

      <Card className="bg-white border-slate-200 shadow-lg rounded-2xl p-10 flex-1 flex items-center justify-center">
        <div className="text-center space-y-6 max-w-lg w-full">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 mx-auto flex items-center justify-center shadow-xl">
            <Upload className="w-10 h-10 text-white" />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-slate-900">Upload Your Documents</h2>
            <p className="text-sm text-slate-600 mt-2">Supports multiple file formats</p>
          </div>

          <label className="flex flex-col gap-2 cursor-pointer group">
            <div className="px-8 py-10 rounded-2xl border-2 border-dashed border-slate-300 group-hover:border-purple-400 transition-all bg-gradient-to-br from-slate-50 to-white group-hover:from-purple-50 group-hover:to-blue-50 group-hover:shadow-md">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                accept=".pdf,.txt,.md,.json,.yaml,.yml,.csv"
              />
              <div className="space-y-3">
                <p className="text-base font-medium text-slate-800">
                  {file ? (
                    <span className="flex items-center justify-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      {file.name}
                    </span>
                  ) : (
                    "Click to select or drag & drop"
                  )}
                </p>
                <p className="text-xs text-slate-500">PDF, TXT, MD, JSON, YAML, CSV</p>
              </div>
            </div>
          </label>

          {file && (
            <Button
              onClick={handleUpload}
              disabled={uploadApi.isLoading}
              className="w-full h-12 text-base font-medium bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg hover:shadow-xl transition-all rounded-xl"
            >
              {uploadApi.isLoading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Uploading...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload Document
                </span>
              )}
            </Button>
          )}

          {uploadApi.isSuccess && (
            <div className="flex gap-2 items-center justify-center text-green-600 bg-green-50 border border-green-200 rounded-xl px-4 py-3 animate-fadeIn">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Document uploaded successfully!</span>
            </div>
          )}
          {uploadApi.isError && (
            <div className="flex gap-2 items-center justify-center text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3 animate-fadeIn">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm font-medium">{uploadApi.error || "Failed to upload document"}</span>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
