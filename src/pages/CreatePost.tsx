import { useState } from "react";
import type { ChangeEvent } from "react";
import "./CreatePost.css";

export default function CreatePost() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedKey, setUploadedKey] = useState<string | null>(null);

  // Handle image selection + upload
  const handleImageChange = async (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setImagePreview(URL.createObjectURL(file));
    setUploading(true);

    try {
      // 1️⃣ Request presigned URL from API Gateway/Lambda
      const res = await fetch(
        `https://nnbvdxpzy8.execute-api.ap-southeast-1.amazonaws.com/prod/upload?filename=${encodeURIComponent(file.name)}`
      );

      if (!res.ok) throw new Error("Failed to fetch presigned URL");

      const data = await res.json();

      if (!data.uploadUrl) {
        throw new Error("No uploadUrl in response");
      }

      const { uploadUrl, key } = data;

      // 2️⃣ Upload file directly to S3
      const upload = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
          "Content-Type": file.type,
        },
        body: file,
      });

      if (!upload.ok) throw new Error("Upload failed");

      setUploadedKey(key);
      alert("✅ Uploaded to S3: " + key);
    } catch (err) {
      console.error("Upload error:", err);
      alert("❌ Upload failed: " + err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="create-post">
      <h1>Create Post</h1>

      <form>
        {/* Image Upload */}
        <input type="file" accept="image/*" onChange={handleImageChange} />

        {uploading && <p>Uploading...</p>}
      </form>

      {/* Preview */}
      <div className="preview">
        <h3>Preview</h3>
        <div className="preview-card">
          {imagePreview && <img src={imagePreview} alt="preview" />}
          {uploadedKey && (
            <p style={{ color: "green" }}>Uploaded as: {uploadedKey}</p>
          )}
        </div>
      </div>
    </div>
  );
}

