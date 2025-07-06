import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const onDrop = (acceptedFiles: File[]) => {
    setFile(acceptedFiles[0]);
    setTitle(acceptedFiles[0]?.name || "");
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/*": [] },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setMessage("");
    setProgress(0);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", title);
      await axios.post(`${API_URL}/lectures/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            setProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
          }
        },
      });
      setMessage("Upload successful! Processing started.");
      setUploading(false);
      setTimeout(() => navigate("/chat"), 1500);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Upload failed.");
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto bg-white p-8 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Upload Lecture Video</h2>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded p-8 text-center cursor-pointer mb-4 ${isDragActive ? "border-blue-400 bg-blue-50" : "border-gray-300"}`}
      >
        <input {...getInputProps()} />
        {file ? (
          <span>{file.name}</span>
        ) : (
          <span>Drag & drop a video file here, or click to select</span>
        )}
      </div>
      <input
        type="text"
        className="w-full border rounded px-3 py-2 mb-4"
        placeholder="Lecture Title (optional)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button
        className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? `Uploading... (${progress}%)` : "Upload"}
      </button>
      {progress > 0 && uploading && (
        <div className="w-full bg-gray-200 rounded h-2 mt-2">
          <div
            className="bg-blue-500 h-2 rounded"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
      {message && <div className="mt-4 text-center text-sm text-gray-700">{message}</div>}
    </div>
  );
};

export default UploadPage; 