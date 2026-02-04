import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser, logout, apiRequest } from "../lib/api";

export default function AdminDashboard() {
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    email: "",
    password: "",
    role: "user",
  });
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [creating, setCreating] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [deleting, setDeleting] = useState(false);
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

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateError("");
    setCreateSuccess("");

    try {
      const { response, data } = await apiRequest("users", {
        method: "POST",
        body: JSON.stringify(createFormData),
      });

      if (response?.status === 401) {
        setCreateError("Session expired. Please log in again.");
        navigate("/login");
        return;
      }

      if (data?.success) {
        setCreateSuccess("User created successfully!");
        setCreateFormData({ email: "", password: "", role: "user" });
        setShowCreateForm(false);
        fetchUsers(); // Refresh the user list
      } else {
        setCreateError(data?.error || "Failed to create user.");
      }
    } catch (err) {
      console.error("Failed to create user:", err);
      setCreateError("Failed to create user.");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!deleteConfirm) return;
    
    setDeleting(true);

    try {
      const { response, data } = await apiRequest(
        `users/${deleteConfirm.id}`,
        {
          method: "DELETE",
        }
      );

      if (response?.status === 401) {
        setError("Session expired. Please log in again.");
        navigate("/login");
        return;
      }

      if (data?.success) {
        setDeleteConfirm(null);
        fetchUsers(); // Refresh the user list
      } else {
        setError(data?.error || "Failed to delete user.");
        setDeleteConfirm(null);
      }
    } catch (err) {
      console.error("Failed to delete user:", err);
      setError("Failed to delete user.");
      setDeleteConfirm(null);
    } finally {
      setDeleting(false);
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
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                Total: {users.length}
              </span>
              <button
                onClick={() => {
                  setShowCreateForm(!showCreateForm);
                  setCreateError("");
                  setCreateSuccess("");
                }}
                className="cursor-pointer rounded-[5px] bg-[#28a745] px-4 py-2 text-white hover:bg-[#218838]"
              >
                {showCreateForm ? "Cancel" : "+ Create User"}
              </button>
            </div>
          </div>

          {createSuccess && (
            <div className="mb-4 rounded-[5px] bg-[#d4edda] p-4 text-[#155724]">
              {createSuccess}
            </div>
          )}

          {showCreateForm && (
            <form
              onSubmit={handleCreateUser}
              className="mb-6 rounded-[10px] border border-gray-200 bg-gray-50 p-6"
            >
              <h3 className="mb-4 text-lg font-semibold">Create New User</h3>

              {createError && (
                <div className="mb-4 rounded-[5px] bg-[#f8d7da] p-4 text-[#721c24]">
                  {createError}
                </div>
              )}

              <div className="mb-4">
                <label className="mb-2 block text-sm font-semibold">
                  Email *
                </label>
                <input
                  type="email"
                  value={createFormData.email}
                  onChange={(e) =>
                    setCreateFormData({ ...createFormData, email: e.target.value })
                  }
                  required
                  className="w-full rounded-[5px] border border-gray-300 px-4 py-2"
                  placeholder="user@example.com"
                />
              </div>

              <div className="mb-4">
                <label className="mb-2 block text-sm font-semibold">
                  Password *
                </label>
                <input
                  type="password"
                  value={createFormData.password}
                  onChange={(e) =>
                    setCreateFormData({ ...createFormData, password: e.target.value })
                  }
                  required
                  minLength={6}
                  className="w-full rounded-[5px] border border-gray-300 px-4 py-2"
                  placeholder="Minimum 6 characters"
                />
              </div>

              <div className="mb-4">
                <label className="mb-2 block text-sm font-semibold">Role *</label>
                <select
                  value={createFormData.role}
                  onChange={(e) =>
                    setCreateFormData({ ...createFormData, role: e.target.value })
                  }
                  className="w-full rounded-[5px] border border-gray-300 px-4 py-2"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={creating}
                className="cursor-pointer rounded-[5px] bg-[#007bff] px-6 py-2 text-white hover:bg-[#0056b3] disabled:bg-gray-400"
              >
                {creating ? "Creating..." : "Create User"}
              </button>
            </form>
          )}

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
                    <th className="px-4 py-3 text-center font-semibold">Actions</th>
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
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() =>
                            setDeleteConfirm({
                              id: u.id,
                              email: u.email,
                            })
                          }
                          disabled={u.id === user.id}
                          title={
                            u.id === user.id
                              ? "You cannot delete your own account"
                              : ""
                          }
                          className={`rounded-[5px] px-3 py-1 text-xs text-white ${
                            u.id === user.id
                              ? "cursor-not-allowed bg-gray-400"
                              : "cursor-pointer bg-[#dc3545] hover:bg-[#c82333]"
                          }`}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {deleteConfirm && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="rounded-[10px] bg-white p-6 shadow-lg">
              <h3 className="mb-4 text-lg font-bold">Confirm Delete</h3>
              <p className="mb-6 text-gray-600">
                Are you sure you want to delete user <strong>{deleteConfirm.email}</strong>?
                This action cannot be undone.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  disabled={deleting}
                  className="cursor-pointer rounded-[5px] bg-gray-400 px-4 py-2 text-white hover:bg-gray-500 disabled:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteUser}
                  disabled={deleting}
                  className="cursor-pointer rounded-[5px] bg-[#dc3545] px-4 py-2 text-white hover:bg-[#c82333] disabled:bg-gray-300"
                >
                  {deleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
