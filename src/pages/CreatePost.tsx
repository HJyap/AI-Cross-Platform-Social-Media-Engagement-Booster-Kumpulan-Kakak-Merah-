import { useState } from "react";
import type { ChangeEvent } from "react";
import "./CreatePost.css";

export default function CreatePost() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // post details returned from Lambda
  const [postData, setPostData] = useState<{
    caption: string;
    hashtags: string[];
    bestTime: string;
    score: number;
  } | null>(null);

  const [loading, setLoading] = useState(false);

  // deployed API Gateway endpoint
  const API_URL = "https://<your-api-id>.execute-api.<region>.amazonaws.com/createPost";

  // image selection and upload to backend pipeline
  const handleImageChange = async (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];

    // show preview
    setImagePreview(URL.createObjectURL(file));
    setLoading(true);

    try {
      // ask backend for a pre-signed upload URL
      const presignRes = await fetch(`${API_URL}/getPresignedUrl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName: file.name, fileType: file.type }),
      });
      const { uploadUrl, fileKey } = await presignRes.json();

      // upload file directly to S3
      await fetch(uploadUrl, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type },
      });

      // call backend to analyze the uploaded file
      const analyzeRes = await fetch(`${API_URL}/analyzePost`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileKey }),
      });

      const data = await analyzeRes.json();
      setPostData(data); // { caption, hashtags, bestTime, score }
    } catch (err) {
      console.error("Error creating post:", err);
      alert("Failed to generate post. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post">
      <h1>Create Post</h1>

      <form>
        <input type="file" accept="image/*" onChange={handleImageChange} />
      </form>

      <div className="preview">
        <h3>Preview</h3>
        <div className="preview-card">
          {imagePreview && <img src={imagePreview} alt="preview" />}

          {loading && <p className="loading">🤖 Analyzing post...</p>}

          {!loading && postData && (
            <div className="post-details">
              <h4>✨ AI-Generated Post</h4>
              <p className="caption">📝 {postData.caption}</p>
              <p className="hashtags">
                {postData.hashtags.map((h, i) => (
                  <span key={i}>{h} </span>
                ))}
              </p>
              <p>📅 Best Time: {postData.bestTime}</p>
              <p>
                ⭐ Post Score: <strong>{postData.score}/100</strong>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}





