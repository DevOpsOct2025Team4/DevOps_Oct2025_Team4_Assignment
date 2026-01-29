import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser, logout } from "../lib/api";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = getStoredUser();
    if (userData) {
      setUser(userData);
    } else {
      navigate("/login");
    }
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      navigate("/login");
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-[#f5f5f5] p-8 font-sans text-slate-900">
      <div className="mx-auto max-w-[800px]">
        <div className="mb-8 flex items-center justify-between">
          <h1>Dashboard</h1>
          <button
            onClick={handleLogout}
            className="cursor-pointer rounded-[5px] bg-[#dc3545] px-4 py-2 text-white"
          >
            Logout
          </button>
        </div>
        <div className="rounded-[10px] bg-[#f8f9fa] p-6">
          <h2>Welcome, {user.email}!</h2>
          <p>Role: <strong>{user.role}</strong></p>
          <p>User ID: {user.id}</p>
        </div>
      </div>
    </div>
  );
}
