import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser, logout } from "../lib/api";

export default function AdminDashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const parsedUser = getStoredUser();
    if (parsedUser) {
      // Check if user has admin role
      if (parsedUser.role !== "admin") {
        navigate("/dashboard");
      } else {
        setUser(parsedUser);
      }
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
      <div className="mx-auto max-w-[1200px]">
        <div className="mb-8 flex items-center justify-between">
          <h1>Admin Dashboard</h1>
          <button
            onClick={handleLogout}
            className="cursor-pointer rounded-[5px] bg-[#dc3545] px-4 py-2 text-white"
          >
            Logout
          </button>
        </div>
        <div className="mb-8 rounded-[10px] bg-[#f8f9fa] p-6">
          <h2>Welcome, Admin {user.email}!</h2>
          <p>Role: <strong>{user.role}</strong></p>
          <p>User ID: {user.id}</p>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
          <div className="rounded-[10px] bg-white p-6 shadow-[0_2px_4px_rgba(0,0,0,0.1)]">
            <h3>Users</h3>
            <p>Manage system users</p>
          </div>
          <div className="rounded-[10px] bg-white p-6 shadow-[0_2px_4px_rgba(0,0,0,0.1)]">
            <h3>Settings</h3>
            <p>Configure system settings</p>
          </div>
          <div className="rounded-[10px] bg-white p-6 shadow-[0_2px_4px_rgba(0,0,0,0.1)]">
            <h3>Reports</h3>
            <p>View system reports</p>
          </div>
        </div>
      </div>
    </div>
  );
}
