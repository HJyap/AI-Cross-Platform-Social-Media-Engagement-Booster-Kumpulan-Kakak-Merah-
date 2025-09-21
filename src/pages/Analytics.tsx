import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./Analytics.css";

const datasets: Record<
  string,
  { name: string; likes: number; comments: number; shares: number }[]
> = {
  Instagram: [
    { name: "Mon", likes: 120, comments: 40, shares: 20 },
    { name: "Tue", likes: 200, comments: 60, shares: 35 },
    { name: "Wed", likes: 150, comments: 50, shares: 25 },
    { name: "Thu", likes: 300, comments: 90, shares: 50 },
    { name: "Fri", likes: 250, comments: 80, shares: 45 },
    { name: "Sat", likes: 400, comments: 120, shares: 70 },
    { name: "Sun", likes: 350, comments: 100, shares: 60 },
  ],
  Reddit: [
    { name: "Mon", likes: 50, comments: 20, shares: 10 },
    { name: "Tue", likes: 75, comments: 30, shares: 15 },
    { name: "Wed", likes: 60, comments: 25, shares: 12 },
    { name: "Thu", likes: 100, comments: 40, shares: 20 },
    { name: "Fri", likes: 90, comments: 35, shares: 18 },
    { name: "Sat", likes: 120, comments: 50, shares: 25 },
    { name: "Sun", likes: 110, comments: 45, shares: 22 },
  ],
  YouTube: [
    { name: "Mon", likes: 300, comments: 100, shares: 50 },
    { name: "Tue", likes: 500, comments: 150, shares: 70 },
    { name: "Wed", likes: 400, comments: 120, shares: 60 },
    { name: "Thu", likes: 700, comments: 200, shares: 100 },
    { name: "Fri", likes: 600, comments: 180, shares: 90 },
    { name: "Sat", likes: 800, comments: 250, shares: 120 },
    { name: "Sun", likes: 750, comments: 220, shares: 110 },
  ],
};

const Analytics = () => {
  const [platform, setPlatform] = useState<keyof typeof datasets>("Instagram");
  const [metric, setMetric] = useState<"likes" | "comments" | "shares">(
    "likes"
  );
  const colors: Record<string, string> = {
    likes: "#E1306C", // pink
    comments: "#36A2EB", // blue
    shares: "#FFCE56", // yellow
  };

  return (
    <div>
      <h1>Analytics</h1>
      <p>Track performance across platforms.</p>
      {/* Platform Selector */}
      <div className="platform-buttons">
        {Object.keys(datasets).map((key) => (
          <button
            key={key}
            className={platform === key ? "active" : ""}
            onClick={() => setPlatform(key as keyof typeof datasets)}
          >
            {key}
          </button>
        ))}
      </div>

      {/* Metric Selector */}
      <div className="metric-buttons">
        {["likes", "comments", "shares"].map((m) => (
          <button
            key={m}
            className={metric === m ? "active" : ""}
            onClick={() => setMetric(m as "likes" | "comments" | "shares")}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      {/* Big Graph */}
      <div className="big-graph">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={datasets[platform]}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey={metric}
              stroke={colors[metric]}
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Analytics;
