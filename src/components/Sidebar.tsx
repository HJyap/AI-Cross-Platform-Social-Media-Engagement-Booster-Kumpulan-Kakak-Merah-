import { Link, useLocation } from "react-router-dom";

const Sidebar = () => {
  const { pathname } = useLocation();

  const menu = [
    { name: "Dashboard", path: "/" },
    { name: "Analytics", path: "/analytics" },
    { name: "Create Post", path: "/createpost" },
    { name: "Profile", path: "/profile" },
  ];

  return (
    <aside className="sidebar">
      <h2>SocialHub</h2>
      <ul>
        {menu.map((item) => (
          <li
            key={item.path}
            className={pathname === item.path ? "active" : ""}
          >
            <Link to={item.path}>{item.name}</Link>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;
