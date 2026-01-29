import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";
import AdminDashboard from "./AdminDashboard";

function Home() {
  const [message, setMessage] = useState("Loading...");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadResult, setUploadResult] = useState(null);

  useEffect(() => {
    fetch("/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Failed to load message"));
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setUploadError("");
    setUploadResult(null);

    if (!file) {
      setUploadError("Please choose a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      if (!response.ok) {
        setUploadError(data.error || "Upload failed.");
      } else {
        setUploadResult(data);
        setFile(null);
      }
    } catch (error) {
      setUploadError("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f5f5]">
      <div className="mx-auto max-w-[720px] p-8 font-sans text-slate-900">
        <h1 className="text-2xl font-semibold">File Upload Demo</h1>
        <p className="mb-6 text-slate-600">Backend says: {message}</p>
        <form
          className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-6"
          onSubmit={handleSubmit}
        >
          <label className="font-semibold text-slate-800" htmlFor="file-input">
          Choose a file to upload
        </label>
        <input
          id="file-input"
          className="rounded-[10px] border border-[#cbd5f5] bg-white p-2 text-base"
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
          <button
            className="cursor-pointer rounded-[10px] bg-blue-600 px-4 py-3 font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400"
            type="submit"
            disabled={uploading}
          >
          {uploading ? "Uploading..." : "Upload to Supabase"}
        </button>
          {uploadError ? <p className="my-2 text-red-700">{uploadError}</p> : null}
        {uploadResult ? (
          <div className="grid gap-1.5 border-t border-slate-200 pt-3">
            <p>
              Uploaded to <strong>{uploadResult.bucket}</strong>
            </p>
              <p className="break-all font-mono text-sm text-slate-800">
                Path: {uploadResult.path}
              </p>
            {uploadResult.url ? (
                <a
                  className="mt-2 inline-block text-blue-600 hover:underline"
                  href={uploadResult.url}
                  target="_blank"
                  rel="noreferrer"
                >
                Open uploaded file
              </a>
            ) : (
                <p className="text-sm text-slate-500">
                  Bucket is private. Use the path to access.
                </p>
            )}
          </div>
        ) : null}
      </form>
        <a className="mt-2 inline-block text-blue-600 hover:underline" href="/health">
          View health status
        </a>
      </div>
    </div>
  );
}

function Health() {
  const [status, setStatus] = useState({
    frontend: false,
    server: false,
    database: false
  });
  const [error, setError] = useState("");

  useEffect(() => {
    setStatus((prev) => ({ ...prev, frontend: true }));

    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => {
        setStatus({
          frontend: true,
          server: true,
          database: Boolean(data.database)
        });
      })
      .catch(() => {
        setError("Health check failed");
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#f5f5f5]">
      <div className="mx-auto max-w-[720px] p-8 font-sans text-slate-900">
        <h1 className="text-2xl font-semibold">Health</h1>
        <div className="my-6 grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-4">
        <div
            className={`rounded-xl border-2 p-5 text-center font-semibold ${status.frontend ? "border-green-700 bg-green-100" : "border-red-700 bg-red-100"
              }`}
        >
          Frontend
        </div>
        <div
            className={`rounded-xl border-2 p-5 text-center font-semibold ${status.server ? "border-green-700 bg-green-100" : "border-red-700 bg-red-100"
              }`}
        >
          Server
        </div>
        <div
            className={`rounded-xl border-2 p-5 text-center font-semibold ${status.database ? "border-green-700 bg-green-100" : "border-red-700 bg-red-100"
              }`}
        >
          Database
        </div>
      </div>
        {error ? <p className="my-2 text-red-700">{error}</p> : null}
        <a className="mt-2 inline-block text-blue-600 hover:underline" href="/">
          Back to home
        </a>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/health" element={<Health />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
