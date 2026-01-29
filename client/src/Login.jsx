import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await login(email, password);

      if (data.success) {
        const role = data.user.role;
        if (role === "admin") {
          navigate("/admin");
        } else {
          navigate("/dashboard");
        }
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#0066cc] via-[#004c99] to-[#003366] p-8 font-sans">
      <div className="w-full max-w-[440px] rounded-2xl bg-white p-12 shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
        <h1 className="mb-2 text-center text-[2.5rem] font-bold tracking-[-0.5px] text-slate-800">
          Log In
        </h1>
        <p className="mb-10 text-center text-base text-slate-500">
          Welcome back! Please enter your credentials
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="email">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your.email@np.edu.sg"
              disabled={loading}
              className="w-full rounded-[10px] border-2 border-slate-200 bg-white px-4 py-3.5 text-base transition placeholder:text-slate-400 focus:border-[#0066cc] focus:outline-none focus:ring-4 focus:ring-[#0066cc]/10 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          <div className="mb-6">
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              disabled={loading}
              className="w-full rounded-[10px] border-2 border-slate-200 bg-white px-4 py-3.5 text-base transition placeholder:text-slate-400 focus:border-[#0066cc] focus:outline-none focus:ring-4 focus:ring-[#0066cc]/10 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          {error && (
            <div className="mb-6 rounded-[10px] border border-red-200 bg-red-50 px-4 py-3.5 text-center text-sm font-medium text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full cursor-pointer rounded-[10px] bg-gradient-to-br from-[#0066cc] to-[#0052a3] px-4 py-4 text-base font-semibold text-white shadow-[0_4px_12px_rgba(0,102,204,0.2)] transition enabled:hover:-translate-y-0.5 enabled:hover:shadow-[0_6px_20px_rgba(0,102,204,0.3)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-slate-500">
          Need help?{" "}
          <a className="font-semibold text-[#0066cc] hover:underline" href="#">
            Contact Support
          </a>
        </p>
      </div>
    </div>
  );
}
