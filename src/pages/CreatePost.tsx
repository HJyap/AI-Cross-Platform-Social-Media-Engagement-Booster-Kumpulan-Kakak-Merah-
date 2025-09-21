import { useState } from "react";
import type { ChangeEvent } from "react";
import "./CreatePost.css";

export default function CreatePost() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // ✅ Hold generated fake post details
  const [fakePost, setFakePost] = useState<{
    caption: string;
    hashtags: string[];
    bestTime: string;
    score: number;
  } | null>(null);

  const [loading, setLoading] = useState(false); // ✅ for delay spinner

  // Handle image selection (no backend call anymore)
  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];

    // Show preview
    setImagePreview(URL.createObjectURL(file));
    setLoading(true); // start loading

    // Simulate AI "thinking"
    setTimeout(() => {
      const hashtagsList = [
        ["#Foodie", "#ViralNow", "#AachenLife", "#Inspo"],
        ["#StudyBreak", "#TechVibes", "#CampusLife", "#GoodEats"],
        ["#NatureShot", "#Relax", "#Motivation", "#Aesthetic"],
      ];
      const randomTags =
        hashtagsList[Math.floor(Math.random() * hashtagsList.length)];

      const times = [
        "Monday 8:00 PM",
        "Wednesday 6:00 PM",
        "Friday 9:00 AM",
        "Sunday 3:00 PM",
      ];
      const bestTime = times[Math.floor(Math.random() * times.length)];

      // ✅ Generate dummy captions
      const captions = [
        "Can’t believe how good this looks 🤩",
        "Just another day, another memory 🌟",
        "Energy boost to keep me going ⚡",
        "The vibes are immaculate ✨",
        "Work hard, snack harder 😋",
      ];
      const caption = captions[Math.floor(Math.random() * captions.length)];

      setFakePost({
        caption,
        hashtags: randomTags,
        bestTime,
        score: Math.floor(Math.random() * 100), // random score 0-99
      });
      setLoading(false); // stop loading
    }, 2000); // ✅ 2s delay
  };

  return (
    <div className="create-post">
      <h1>Create Post</h1>

      <form>
        {/* Image Upload */}
        <input type="file" accept="image/*" onChange={handleImageChange} />
      </form>

      {/* Preview */}
      <div className="preview">
        <h3>Preview</h3>
        <div className="preview-card">
          {imagePreview && <img src={imagePreview} alt="preview" />}

          {/* Loading spinner */}
          {loading && <p className="loading">🤖 Generating post...</p>}

          {/* ✅ Fake post details */}
          {!loading && fakePost && (
            <div className="post-details">
              <h4>✨ AI-Generated Post</h4>
              <p className="caption">📝 {fakePost.caption}</p>
              <p className="hashtags">
                {fakePost.hashtags.map((h, i) => (
                  <span key={i}>{h} </span>
                ))}
              </p>
              <p>📅 Best Time: {fakePost.bestTime}</p>
              <p>
                ⭐ Post Score: <strong>{fakePost.score}/100</strong>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}




