import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ChatPage from "./pages/ChatPage";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow mb-6">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              Lecture Intelligence
            </Link>
            <div className="space-x-4">
              <Link to="/" className="text-gray-700 hover:text-blue-600">Upload</Link>
              <Link to="/chat" className="text-gray-700 hover:text-blue-600">Chat</Link>
            </div>
          </div>
        </nav>
        <main className="container mx-auto px-4">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/chat" element={<ChatPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
