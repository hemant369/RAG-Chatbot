import { useEffect, useState } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Trash2, FileText } from "lucide-react";
import { listDocuments, deleteDocument } from "../../api/client";
import { useApiCall } from "../../hooks/useApiCall";

export function LibraryView() {
  const [docs, setDocs] = useState<any[]>([]);

  const fetchApi = useApiCall({
    onSuccess: (documents) => {
      setDocs(documents);
    },
  });

  const deleteApi = useApiCall();

  useEffect(() => {
    fetchApi.execute(() => listDocuments());
  }, []);

  async function handleDelete(id: string) {
    await deleteApi.execute(() => deleteDocument(id));
    setDocs((d) => d.filter((doc) => doc.doc_id !== id));
  }

  return (
    <div className="flex flex-col h-full p-8 gap-6 bg-gradient-to-br from-slate-50 to-white">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
          Document Library
        </h1>
        <p className="text-sm text-slate-600 mt-1">Manage and organize your indexed documents</p>
      </div>

      <Card className="bg-white border-slate-200 shadow-lg rounded-2xl p-6 flex-1 overflow-auto">
        {fetchApi.isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto" />
              <p className="text-slate-600 font-medium">Loading documents...</p>
            </div>
          </div>
        ) : docs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-3">
              <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto">
                <FileText className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-slate-600 font-medium">No documents yet</p>
              <p className="text-sm text-slate-500">Upload documents to get started</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {docs.map((doc) => (
              <div
                key={doc.doc_id}
                className="group flex items-center justify-between p-4 rounded-xl bg-gradient-to-br from-white to-slate-50 border border-slate-200 hover:border-purple-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">{doc.filename}</p>
                    <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                      {doc.chunk_count} chunks indexed
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => handleDelete(doc.doc_id)}
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
