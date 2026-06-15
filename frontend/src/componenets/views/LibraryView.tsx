import { useEffect, useState } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Trash2, FileText } from "lucide-react";
import { listDocuments, deleteDocument } from "../../api/client";

export function LibraryView() {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocs();
  }, []);

  async function fetchDocs() {
    try {
      const documents = await listDocuments();
      setDocs(documents);
    } catch (e) {
      console.error("Failed to fetch documents:", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDocument(id);
      setDocs((d) => d.filter((doc) => doc.doc_id !== id));
    } catch (e) {
      console.error("Failed to delete document:", e);
    }
  }

  return (
    <div className="flex flex-col h-full p-6 gap-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Document Library</h1>
        <p className="text-sm text-slate-500">Manage your indexed documents</p>
      </div>

      <Card className="bg-white border-slate-200 shadow-sm p-6 flex-1 overflow-auto">
        {loading ? (
          <div className="text-center text-slate-500">Loading...</div>
        ) : docs.length === 0 ? (
          <div className="text-center text-slate-500">No documents yet</div>
        ) : (
          <div className="space-y-2">
            {docs.map((doc) => (
              <div
                key={doc.doc_id}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200 hover:bg-slate-100 transition"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileText className="w-5 h-5 text-slate-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{doc.filename}</p>
                    <p className="text-xs text-slate-500">{doc.chunk_count} chunks</p>
                  </div>
                </div>
                <Button
                  onClick={() => handleDelete(doc.doc_id)}
                  variant="ghost"
                  size="sm"
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
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
