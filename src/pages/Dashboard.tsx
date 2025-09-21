import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./Dashboard.css"; 

const data = [
  { name: "Mon", value: 30 },
  { name: "Tue", value: 45 },
  { name: "Wed", value: 28 },
  { name: "Thu", value: 55 },
  { name: "Fri", value: 38 },
  { name: "Sat", value: 65 },
  { name: "Sun", value: 50 },
];

const trends = [
  "#ReactJS",
  "#OpenAI",
  "#SocialMedia",
  "#ViteJS",
  "#EngagementBoost",
];

const newestPost = {
  platform: "Twitter",
  content: "Excited to launch my new project 🚀 Stay tuned!",
  time: "2 hours ago",
};

const Dashboard = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Overview of scheduled posts and engagement activity.</p>
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <div style={{ flex: 1, height: 200, background: "#fff", padding: 10, borderRadius: 8 }}>
          <h3 style={{ margin: "0 0 10px" }}>Likes</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: 1, height: 200, background: "#fff", padding: 10, borderRadius: 8 }}>
          <h3 style={{ margin: "0 0 10px" }}>Comments</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#82ca9d" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: 1, height: 200, background: "#fff", padding: 10, borderRadius: 8 }}>
          <h3 style={{ margin: "0 0 10px" }}>Shares</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#ffc658" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

            <div className="bottom-row">
        {/* Trends */}
        <div className="trends-card">
          <h3>🔥 Today’s Top 5 Trends</h3>
          <ul>
            {trends.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

        {/* Newest Post */}
        <div className="post-card">
          <h3>📝 Your Newest Post</h3>
          <p><strong>{newestPost.platform}</strong></p>
          <p>{newestPost.content}</p>
          <small>{newestPost.time}</small>
        </div>
      </div>
      
    </div>
  );
};

export default Dashboard;
