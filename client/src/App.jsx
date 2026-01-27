import { useEffect, useState } from "react";
import "./App.css";

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
    <div className="app">
      <h1>File Upload Demo</h1>
      <p className="subtitle">Backend says: {message}</p>
      <form className="upload-card" onSubmit={handleSubmit}>
        <label className="upload-label" htmlFor="file-input">
          Choose a file to upload
        </label>
        <input
          id="file-input"
          className="upload-input"
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <button className="upload-button" type="submit" disabled={uploading}>
          {uploading ? "Uploading..." : "Upload to Supabase"}
        </button>
        {uploadError ? <p className="error">{uploadError}</p> : null}
        {uploadResult ? (
          <div className="upload-result">
            <p>
              Uploaded to <strong>{uploadResult.bucket}</strong>
            </p>
            <p className="mono">Path: {uploadResult.path}</p>
            {uploadResult.url ? (
              <a className="link" href={uploadResult.url} target="_blank" rel="noreferrer">
                Open uploaded file
              </a>
            ) : (
              <p className="muted">Bucket is private. Use the path to access.</p>
            )}
          </div>
        ) : null}
      </form>
      <a className="link" href="/health">
        View health status
      </a>
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
    <div className="app">
      <h1>Health</h1>
      <div className="status-grid">
        <div
          className={`status-card ${status.frontend ? "status-card--ok" : "status-card--bad"
            }`}
        >
          Frontend
        </div>
        <div
          className={`status-card ${status.server ? "status-card--ok" : "status-card--bad"
            }`}
        >
          Server
        </div>
        <div
          className={`status-card ${status.database ? "status-card--ok" : "status-card--bad"
            }`}
        >
          Database
        </div>
      </div>
      {error ? <p className="error">{error}</p> : null}
      <a className="link" href="/">
        Back to home
      </a>
    </div>
  );
}

export default function App() {
  const isHealth = window.location.pathname === "/health";
  return isHealth ? <Health /> : <Home />;
}
