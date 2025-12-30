import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import api from "@/lib/api";
import ExtensionHelper from "./ExtensionHelper";

type UploadResponse = {
  upload_id: string;
  filename: string;
  stored_path: string;
  status: string;
  created_at: string;
  processed_at?: string | null;
  row_count?: number | null;
};

function UploadPanel() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post<UploadResponse>("/uploads/csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["metrics"] });
      setSelectedFile(null);
      setFileName(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setFileName(file?.name ?? null);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  return (
    <div className="grid gap-6">
      <ExtensionHelper stepLabel="Step 1" />
      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Step 2</p>
          <h2 className="text-2xl font-semibold text-slate-900">Upload Sportsbet CSV</h2>
          <p className="text-sm text-slate-600">
            Sportsbet’s default download only includes your most recent 50 transactions. Use the extension above to
            capture a complete CSV, then upload it here. We keep the file on this device only.
          </p>
        </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label
          className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-brand-200 bg-brand-50/50 p-6 text-center text-slate-600 transition hover:border-brand-500 hover:bg-white"
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            const file = event.dataTransfer.files?.[0];
            if (!file) return;
            setSelectedFile(file);
            setFileName(file.name);
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileChange}
            disabled={uploadMutation.isPending}
          />
          <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-600">
            CSV only
          </span>
          <span className="text-lg font-semibold text-slate-900">
            {selectedFile ? `Selected: ${fileName}` : "Click to browse or drag & drop"}
          </span>
          <span className="text-xs text-slate-500">Max 25MB · incremental uploads supported</span>
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            className="inline-flex items-center justify-center rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={!selectedFile || uploadMutation.isPending}
          >
            {uploadMutation.isPending ? "Uploading…" : "Upload CSV"}
          </button>
          {selectedFile && !uploadMutation.isPending && (
            <p className="text-sm text-slate-600">Ready to upload {fileName}</p>
          )}
        </div>
      </form>

      <div className="mt-4 min-h-[24px] text-sm">
        {uploadMutation.isError && (
          <p className="text-rose-600">Upload failed. Please verify the CSV export and try again.</p>
        )}
        {uploadMutation.isSuccess && (
          <p className="text-emerald-600">
            Ingested {uploadMutation.data.row_count ?? 0} rows from {uploadMutation.data.filename}. Metrics refreshed.
          </p>
        )}
      </div>
      </section>
    </div>
  );
}

export default UploadPanel;
