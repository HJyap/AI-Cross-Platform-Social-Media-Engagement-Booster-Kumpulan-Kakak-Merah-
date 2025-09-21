import { useState } from "react";
import type { ChangeEvent } from "react";
import "./CreatePost.css";

export default function CreatePost() {
  const [text, setText] = useState("");
  const [image, setImage] = useState<string | null>(null);

  // Handle text input
  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  // Handle image upload
  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImage(URL.createObjectURL(file)); // preview image locally
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Post created! (dummy for now)");
    // Later: send `text` + `image` to backend
  };

  return (
    <div className="create-post">
      <h1>Create Post</h1>

      <form onSubmit={handleSubmit}>
        {/* Text Input */}
        <textarea
          placeholder="What's on your mind?"
          value={text}
          onChange={handleTextChange}
        />

        {/* Image Upload */}
        <input type="file" accept="image/*" onChange={handleImageChange} />

        <button type="submit">Post</button>
      </form>

      {/* Preview */}
      <div className="preview">
        <h3>Post Preview</h3>
        <div className="preview-card">
          {text && <p>{text}</p>}
          {image && <img src={image} alt="preview" />}
        </div>
      </div>
    </div>
  );
}
