import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser, logout, apiRequest } from "../lib/api";

export default function AdminDashboard() {
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const parsedUser = getStoredUser();
    if (parsedUser) {
      // Check if user has admin role
      if (parsedUser.role !== "admin") {
        navigate("/dashboard");
      } else {
        setUser(parsedUser);
        fetchUsers();
      }
    } else {
      navigate("/login");
    }
  }, [navigate]);

  const fetchUsers = async () => {
    try {
      const { response, data } = await apiRequest("users");

      if (response?.status === 401) {
        setError("Session expired. Please log in again.");
        navigate("/login");
        return;
      }

      if (data?.success) {
        setUsers(data.users || []);
      } else {
        setError(data?.error || "Failed to fetch users.");
      }
    } catch (err) {
      console.error("Failed to fetch users:", err);
      setError("Failed to fetch users.");
    } finally {
      setLoading(false);
    }
  };

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
          <p>
            Role: <strong>{user.role}</strong>
          </p>
          <p>User ID: {user.id}</p>
        </div>

        <div className="mb-8 rounded-[10px] bg-white p-6 shadow-[0_2px_4px_rgba(0,0,0,0.1)]">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold">Registered Users</h2>
            <span className="text-sm text-gray-600">
              Total: {users.length}
            </span>
          </div>

          {error && (
            <div className="mb-4 rounded-[5px] bg-[#f8d7da] p-4 text-[#721c24]">
              {error}
            </div>
          )}

          {loading ? (
            <div className="py-8 text-center text-gray-500">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              No registered users found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="px-4 py-3 text-left font-semibold">Email</th>
                    <th className="px-4 py-3 text-left font-semibold">Role</th>
                    <th className="px-4 py-3 text-left font-semibold">User ID</th>
                    <th className="px-4 py-3 text-left font-semibold">Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr
                      key={u.id}
                      className="border-b border-gray-200 hover:bg-gray-50"
                    >
                      <td className="px-4 py-3">{u.email}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-[5px] px-3 py-1 text-sm font-semibold ${
                            u.role === "admin"
                              ? "bg-[#d4edda] text-[#155724]"
                              : "bg-[#e2e3e5] text-[#383d41]"
                          }`}
                        >
                          {u.role}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-gray-600">
                        {u.id}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {u.created_at
                          ? new Date(u.created_at).toLocaleDateString()
                          : "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
