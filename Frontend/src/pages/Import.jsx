import React, { useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function ImportPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [columns, setColumns] = useState([]);
  const [mapping, setMapping] = useState({});
  const [step, setStep] = useState("upload"); // upload → map → import
  const [loading, setLoading] = useState(false);

  const handlePreview = async () => {
    if (!file) return alert("Select a file first");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await api.post("/api/admin/preview-import", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setColumns(res.data.columns || []);
      setPreview(res.data.preview || []);
      setStep("map");
    } catch {
      alert("Failed to preview file");
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append(
      "mapping_req",
      JSON.stringify({ mapping, create_departments: true })
    );
    try {
      const res = await api.post("/api/admin/import-file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("Import completed!");
      console.log(res.data);
      setStep("upload");
      setFile(null);
      setPreview([]);
    } catch {
      alert("Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Bulk Import</h1>

      {step === "upload" && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
          <h2 className="font-medium mb-2">Upload Excel or CSV</h2>
          <input
            type="file"
            accept=".csv,.xls,.xlsx"
            onChange={(e) => setFile(e.target.files[0])}
            className="border px-3 py-1 rounded-md w-full mb-2"
          />
          <button
            onClick={handlePreview}
            disabled={loading}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            {loading ? "Loading..." : "Preview"}
          </button>
        </div>
      )}

      {step === "map" && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
          <h2 className="font-medium mb-3">Column Mapping</h2>
          <p className="text-sm mb-2">Map your Excel columns:</p>

          {["name", "email", "role", "department", "class", "section", "password"].map((key) => (
            <div key={key} className="flex gap-2 mb-2">
              <span className="w-32 font-medium capitalize">{key}</span>
              <select
                onChange={(e) =>
                  setMapping({ ...mapping, [key]: e.target.value })
                }
                className="border px-2 py-1 rounded-md flex-1"
              >
                <option value="">Select Column</option>
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          ))}

          <button
            onClick={handleImport}
            disabled={loading}
            className="bg-green-600 text-white px-3 py-1 rounded-md mt-3"
          >
            {loading ? "Importing..." : "Import"}
          </button>

          <h3 className="font-medium mt-6 mb-2">Preview (first 10 rows)</h3>
          <div className="overflow-auto max-h-64 border rounded-md">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  {columns.map((col) => (
                    <th key={col} className="border px-2 py-1">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i}>
                    {columns.map((col) => (
                      <td key={col} className="border px-2 py-1">
                        {row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Layout>
  );
}
