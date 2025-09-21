import { useState } from "react";
import "./Profile.css";

const storedUser = localStorage.getItem("user");
const initialUser = storedUser
  ? JSON.parse(storedUser)
  : {
      userId: "",
      name: "Guest",
      email: "guest@example.com",
      bio: "Not signed in",
      avatarUrl: "https://i.pravatar.cc/150?img=1",
    };

export default function Profile() {
  const [user, setUser] = useState(initialUser);
  const [message, setMessage] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    try {
      const response = await fetch(
        `https://7s1895lwg3.execute-api.ap-southeast-1.amazonaws.com/dev/profile/${user.userId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: user.name,
            bio: user.bio,
            avatarUrl: user.avatarUrl,
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        setMessage(data.error || "Failed to update profile");
        return;
      }

      // Update localStorage
      localStorage.setItem("user", JSON.stringify(data.user));
      setMessage("Profile updated successfully!");
    } catch (err) {
      console.error(err);
      setMessage("Network error");
    }
  };

  return (
    <div className="profile">
      <div className="profile-card">
        <img
          src={user.avatarUrl || "https://i.pravatar.cc/150?img=1"}
          alt="avatar"
        />

        <input
          type="text"
          name="name"
          value={user.name}
          onChange={handleChange}
          placeholder="Full Name"
        />
        <input
          type="text"
          name="avatarUrl"
          value={user.avatarUrl}
          onChange={handleChange}
          placeholder="Avatar URL"
        />
        <textarea
          name="bio"
          value={user.bio}
          onChange={handleChange}
          placeholder="Bio"
        />
        <button onClick={handleSave}>Save</button>
        {message && <p>{message}</p>}
      </div>
    </div>
  );
}
