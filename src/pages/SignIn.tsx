import { Link } from "react-router-dom"; // add at top
import { useState } from "react";
import "./Auth.css";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      alert("No account found. Please sign up first.");
      return;
    }

    try {
      const user = JSON.parse(storedUser);
      if (user.email === email && user.password === password) {
        localStorage.setItem("loggedIn", "true");
        window.location.href = "/"; // redirect to dashboard
      } else {
        alert("Invalid email or password.");
      }
    } catch (err) {
      console.error("Error parsing user data:", err);
      alert("Something went wrong. Please sign up again.");
      localStorage.removeItem("user");
    }
  };

  return (
    <div className="auth">
      <form onSubmit={handleSubmit} className="auth-card">
        <h2>Sign In</h2>
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
          Don’t have an account? <Link to="/signup">Sign Up</Link>
        </p>
      </form>
    </div>
  );
}
