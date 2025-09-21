import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    console.log("Signing in with:", email, password);

    try {
      const response = await fetch(
        "https://7s1895lwg3.execute-api.ap-southeast-1.amazonaws.com/dev/signin",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Sign in failed");
        return;
      }

      // Save user data to localStorage
      localStorage.setItem("user", JSON.stringify(data.user));

      // Redirect to dashboard
      navigate("/");
    } catch (err) {
      setError("Network error");
      console.error(err);
    }
  };

  return (
    <div className="auth">
      <form onSubmit={handleSubmit} className="auth-card">
        <h2>Sign In</h2>
        {error && <p className="error">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Sign In</button>
        <p>
          Don't have an account? <a href="/signup">Sign Up</a>
        </p>
      </form>
    </div>
  );
}
