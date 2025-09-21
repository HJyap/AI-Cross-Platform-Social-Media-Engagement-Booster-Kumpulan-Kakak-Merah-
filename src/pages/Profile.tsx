import "./Profile.css";

const user = {
  name: "John Doe",
  email: "john@example.com",
  bio: "Social media enthusiast 🚀 | Content creator | Coffee lover",
  avatar: "https://i.pravatar.cc/150?img=3", // placeholder avatar
};

export default function Profile() {
  return (
    <div className="profile">
      <div className="profile-card">
        <img src={user.avatar} alt="avatar" />
        <h2>{user.name}</h2>
        <p>{user.email}</p>
        <p>{user.bio}</p>

        <button
          onClick={() => {
            localStorage.removeItem("user");
            window.location.href = "/signin";
          }}
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}
