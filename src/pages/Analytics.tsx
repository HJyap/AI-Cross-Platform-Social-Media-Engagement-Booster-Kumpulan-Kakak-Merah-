import React, { useEffect, useState } from "react";
import "./Analytics.css";

// Define types for Instagram stats
interface InstagramPost {
  media_url: string;
  caption: string;
  insights: {
    likes: number;
    comments: number;
    shares: number;
    reach: number;
  };
  timestamp: string;
}

const Analytics = () => {
  const [instagramPosts, setInstagramPosts] = useState<InstagramPost[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInstagram = async () => {
      try {
        const response = await fetch("http://localhost:8000/instagram-stats2");
        const data = await response.json();
        if (data.instagram_statistics) {
          setInstagramPosts(data.instagram_statistics);
        } else {
          setError("No data found");
        }
      } catch (error) {
        setError("Error fetching data");
      }
    };

    fetchInstagram();
  }, []);

  return (
    <div>
      <h1>Social Media Analytics</h1>
      <p>Detailed Instagram Engagement</p>

      {/* Instagram Posts Display */}
      <div className="posts-container">
        {error ? (
          <p>{error}</p>
        ) : (
          instagramPosts.map((post, index) => (
            <div key={index} className="post-card">
              <img src={post.media_url} alt={`Post ${index}`} className="post-image" />
              <div className="post-info">
                <p className="caption">{post.caption}</p>
                <p><strong>Likes:</strong> {post.insights.likes}</p>
                <p><strong>Comments:</strong> {post.insights.comments}</p>
                <p><strong>Shares:</strong> {post.insights.shares}</p>
                <p><strong>Reach:</strong> {post.insights.reach}</p>
                <small>Posted on: {new Date(post.timestamp).toLocaleString()}</small>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Analytics;
