import React, { useEffect, useState } from "react";

// Define types for the data
interface RedditPost {
  title: string;
  url: string;
  score: number;
}

const RedditTrends: React.FC = () => {
  const [trends, setTrends] = useState<RedditPost[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRedditTrends = async () => {
      try {
        const response = await fetch("http://localhost:8000/reddit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode: "trending",       // Request trending data
            subreddit: "all",       // Fetch trends from "all" subreddit
            time: "day",            // Time range: day, week, etc.
            limit: 5,               // Limit to top 5 results
          }),
        });

        const data = await response.json();

        if (data.reddit_posts) {
          setTrends(data.reddit_posts);  // Store the fetched trends
        } else {
          setError("Error fetching Reddit trends");
        }
      } catch (error) {
        setError("Error fetching data");
      }
    };

    fetchRedditTrends();
  }, []); // Fetch data once when the component mounts

  return (
    <div>
      {error ? (
        <p>{error}</p>
      ) : (
        <ul>
          {trends.map((post, index) => (
            <li key={index}>
              <a href={post.url} target="_blank" rel="noopener noreferrer">
                {post.title}
              </a> - Score: {post.score}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RedditTrends;
