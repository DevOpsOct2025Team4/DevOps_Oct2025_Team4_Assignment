import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useEffect, useState } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";
import AdminDashboard from "./AdminDashboard";
import { apiRequest, getStoredUser } from "../lib/api";

function Health() {
  const [status, setStatus] = useState({
    frontend: false,
    server: false,
    database: false,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    setStatus((prev) => ({ ...prev, frontend: true }));

    apiRequest("health", { auth: false })
      .then(({ data }) => {
        setStatus({
          frontend: true,
          server: true,
          database: Boolean(data?.database),
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
            className={`rounded-xl border-2 p-5 text-center font-semibold ${
              status.frontend
                ? "border-green-700 bg-green-100"
                : "border-red-700 bg-red-100"
            }`}
          >
            Frontend
          </div>
          <div
            className={`rounded-xl border-2 p-5 text-center font-semibold ${
              status.server
                ? "border-green-700 bg-green-100"
                : "border-red-700 bg-red-100"
            }`}
          >
            Server
          </div>
          <div
            className={`rounded-xl border-2 p-5 text-center font-semibold ${
              status.database
                ? "border-green-700 bg-green-100"
                : "border-red-700 bg-red-100"
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

function RequireAuth({ children }) {
  const user = getStoredUser();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function RequireAdmin({ children }) {
  const user = getStoredUser();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

function RootRedirect() {
  const user = getStoredUser();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role === "admin") {
    return <Navigate to="/admin" replace />;
  }
  return <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/health" element={<Health />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminDashboard />
            </RequireAdmin>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
