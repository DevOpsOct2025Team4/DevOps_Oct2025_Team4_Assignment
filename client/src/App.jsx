import { useEffect, useState } from "react";
import "./App.css";

function Home() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Failed to load message"));
  }, []);

  return (
    <div className="app">
      <h1>Vite + React</h1>
      <p>Backend says: {message}</p>
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
