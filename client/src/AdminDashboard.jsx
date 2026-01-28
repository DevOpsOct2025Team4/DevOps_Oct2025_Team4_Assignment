import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      const parsedUser = JSON.parse(userData);
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
    const token = localStorage.getItem("access_token");
    
    try {
      await fetch("/api/logout", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      // Clear local storage and redirect
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      navigate("/login");
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
          <h1>Admin Dashboard</h1>
          <button onClick={handleLogout} style={{
            padding: "0.5rem 1rem",
            background: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}>
            Logout
          </button>
        </div>
        <div style={{ background: "#f8f9fa", padding: "1.5rem", borderRadius: "10px", marginBottom: "2rem" }}>
          <h2>Welcome, Admin {user.email}!</h2>
          <p>Role: <strong>{user.role}</strong></p>
          <p>User ID: {user.id}</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
          <div style={{ background: "white", padding: "1.5rem", borderRadius: "10px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
            <h3>Users</h3>
            <p>Manage system users</p>
          </div>
          <div style={{ background: "white", padding: "1.5rem", borderRadius: "10px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
            <h3>Settings</h3>
            <p>Configure system settings</p>
          </div>
          <div style={{ background: "white", padding: "1.5rem", borderRadius: "10px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
            <h3>Reports</h3>
            <p>View system reports</p>
          </div>
        </div>
      </div>
    </div>
  );
}
