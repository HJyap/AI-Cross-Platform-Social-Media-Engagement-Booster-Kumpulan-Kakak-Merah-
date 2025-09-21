import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { PieChart, Pie, Cell, Legend } from "recharts";
import RedditTrends from "./RedditTrends"; // Import the RedditTrends component
import "./Dashboard.css";

// Define types for Instagram, Reddit, and YouTube Aggregated Stats
interface InstagramStats {
  likes: number;
  comments: number;
  shares: number;
}

interface RedditStats {
  upvotes: number;
  comments: number;
  score: number;
}

interface YouTubeStats {
  views: number;
  likes: number;
  comments: number;
  shares: number;
}

const Dashboard = () => {
  const [instagramStats, setInstagramStats] = useState<InstagramStats | null>(null);
  const [redditStats, setRedditStats] = useState<RedditStats | null>(null);
  const [youtubeStats, setYoutubeStats] = useState<YouTubeStats | null>(null);

  useEffect(() => {
    const fetchInstagram = async () => {
      const response = await fetch("http://localhost:8000/instagram-stats");
      const data = await response.json();
      setInstagramStats(data.instagram_stats);
    };

    const fetchReddit = async () => {
      const response = await fetch("http://localhost:8000/reddit-stats");
      const data = await response.json();
      setRedditStats(data.reddit_engagement_stats);
    };

    const fetchYouTube = async () => {
      const response = await fetch("http://localhost:8000/youtube-stats");
      const data = await response.json();
      setYoutubeStats(data.youtube_video_stats);
    };

    fetchInstagram();
    fetchReddit();
    fetchYouTube();
  }, []);

  // Data for Pie Charts
  const instagramData = [
    { name: "Likes", value: instagramStats?.likes || 0, fill: "#8884d8" },
    { name: "Comments", value: instagramStats?.comments || 0, fill: "#82ca9d" },
    { name: "Shares", value: instagramStats?.shares || 0, fill: "#ffc658" },
  ];

    // Data for Reddit Pie Chart
  const redditData = [
    { name: "Upvotes", value: redditStats?.upvotes || 0, fill: "#82ca9d" },
    { name: "Comments", value: redditStats?.comments || 0, fill: "#8884d8" },
    { name: "Score", value: redditStats?.score || 0, fill: "#ffc658" },
  ];

  // Data for Line Charts
  const lineData = [
    { name: "Mon", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Tue", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Wed", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Thu", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Fri", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Sat", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
    { name: "Sun", likes: instagramStats?.likes || 0, upvotes: redditStats?.upvotes || 0, views: youtubeStats?.views || 0 },
  ];

  return (
    <div className="dashboard">
      <h1>Social Media Dashboard</h1>
      <p>Overview of social media engagement activity.</p>

      <div className="dashboard-content">
        {/* Instagram Pie Chart */}
        <div className="stats-card">
          <h3>Instagram Stats</h3>
          {instagramStats ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={instagramData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {instagramData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p>Loading...</p>
          )}
        </div>

    {/* Reddit Pie Chart */}
    <div className="stats-card">
      <h3>Reddit Engagement</h3>
      {redditStats ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={redditData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
              labelLine={false} // Disable label lines for a cleaner look
            >
              {redditData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip />
            <Legend
              verticalAlign="bottom"
              align="center"
              iconType="circle"
              wrapperStyle={{
                marginTop: '20px', // Adjust margin to ensure the legend has space
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p>Loading...</p>
      )}
    </div>

        {/* YouTube Stats Line Chart */}
        <div className="stats-card">
          <h3>YouTube Video Stats</h3>
          {youtubeStats ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="views" stroke="#ffc658" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>Loading...</p>
          )}
        </div>
      </div>

                {/* Trending Section */}
      <div className="trends-card">
        <h3>🔥 Today’s Top 5 Trends</h3>
        <RedditTrends /> {/* Reddit Trends Component */}
      </div>
    </div>
  );
};

export default Dashboard;
