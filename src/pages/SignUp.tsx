import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";

export default function SignUp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch(
        "https://7s1895lwg3.execute-api.ap-southeast-1.amazonaws.com/dev/signup",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Signup failed");
        return;
      }

      // Signup successful → navigate to Sign In
      navigate("/signin");
    } catch (err) {
      setError("Network error");
      console.error(err);
    }
  };

  return (
    <div className="auth">
      <form onSubmit={handleSubmit} className="auth-card">
        <h2>Sign Up</h2>
        {error && <p className="error">{error}</p>}
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
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
        <button type="submit">Sign Up</button>
        <p>
          Already have an account? <a href="/signin">Sign In</a>
        </p>
      </form>
    </div>
  );
}
