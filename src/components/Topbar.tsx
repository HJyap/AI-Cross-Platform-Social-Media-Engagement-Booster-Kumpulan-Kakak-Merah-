
const Topbar = () => {
  return (
    <header className="topbar">
      <input type="text" placeholder="Search..." className="search" />
      <div className="user-menu">
        <span className="username">John Doe</span>
        <img
          src="https://via.placeholder.com/32"
          alt="User Avatar"
          className="avatar"
        />
      </div>
    </header>
  );
};

export default Topbar;
