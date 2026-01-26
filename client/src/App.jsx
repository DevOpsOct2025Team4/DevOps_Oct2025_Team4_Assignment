import { useEffect, useState } from "react";
import "./App.css";

export default function App() {
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
    </div>
  );
}
