import "./Profile.css";

const storedUser = localStorage.getItem("user");
const user = storedUser
  ? JSON.parse(storedUser)
  : {
      name: "Guest",
      email: "guest@example.com",
      bio: "Not signed in",
      avatar: "https://i.pravatar.cc/150?img=1",
    };

export default function Profile() {
  return (
    <div className="profile">
      <div className="profile-card">
        <img src={user.avatar} alt="avatar" />
        <h2>{user.name}</h2>
        <p>{user.email}</p>
        <p>{user.bio}</p>
      </div>
    </div>
  );
}
