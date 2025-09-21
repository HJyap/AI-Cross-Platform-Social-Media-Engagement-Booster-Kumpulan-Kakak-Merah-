import { Outlet, Link } from "react-router-dom";
import "./MainLayout.css";
import Logo from "../assets/logo.svg";

export default function MainLayout() {
  return (
    <div className="main-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <img src={Logo} alt="App logo" className="logo-img" />
        </div>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/analytics">Analytics</Link>
          <Link to="/create">Create Post</Link>
          <Link to="/profile">Profile</Link>
        </nav>
      </aside>

      {/* Main content area */}
      <div className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <h3>Welcome Back!</h3>
          <button
            onClick={() => {
              localStorage.removeItem("loggedIn");
              window.location.href = "/signin";
            }}
          >
            Log Out
          </button>
        </header>

        {/* Page content */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
