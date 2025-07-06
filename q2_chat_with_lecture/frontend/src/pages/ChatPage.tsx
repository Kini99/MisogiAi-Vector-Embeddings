import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

interface Lecture {
  id: number;
  title: string;
  status: string;
  duration?: number;
}

interface ChatMessage {
  role: string;
  content: string;
  timestamp_references?: string[];
}

const ChatPage: React.FC = () => {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [selectedLecture, setSelectedLecture] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axios.get(`${API_URL}/lectures`).then((res) => {
      setLectures(res.data.filter((l: Lecture) => l.status === "completed"));
    });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSelectLecture = (id: number) => {
    setSelectedLecture(id);
    setMessages([]);
  };

  const handleSend = async () => {
    if (!input.trim() || !selectedLecture) return;
    setLoading(true);
    setMessages((msgs) => [...msgs, { role: "user", content: input }]);
    try {
      const res = await axios.post(`${API_URL}/chat/quick-chat?lecture_id=${selectedLecture}`, {
        question: input,
      });
      setMessages((msgs) => [
        ...msgs,
        {
          role: "assistant",
          content: res.data.response,
          timestamp_references: res.data.timestamp_references,
        },
      ]);
    } catch (err: any) {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: err.response?.data?.detail || "Error." },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Chat with Your Lecture</h2>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Select a Lecture:</label>
        <select
          className="w-full border rounded px-3 py-2"
          value={selectedLecture || ""}
          onChange={(e) => handleSelectLecture(Number(e.target.value))}
        >
          <option value="">-- Choose a lecture --</option>
          {lectures.map((lecture) => (
            <option key={lecture.id} value={lecture.id}>
              {lecture.title} ({Math.round((lecture.duration || 0) / 60)} min)
            </option>
          ))}
        </select>
      </div>
      {selectedLecture && (
        <div className="border rounded p-4 h-96 overflow-y-auto bg-gray-50 mb-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-3 ${msg.role === "user" ? "text-right" : "text-left"}`}>
              <div
                className={`inline-block px-4 py-2 rounded-lg ${
                  msg.role === "user"
                    ? "bg-blue-100 text-blue-900"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.content}
                {msg.timestamp_references && msg.timestamp_references.length > 0 && (
                  <div className="text-xs text-blue-600 mt-1">
                    {msg.timestamp_references.map((ts, i) => (
                      <span key={i} className="mr-2">[{ts}]</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
      )}
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          type="text"
          placeholder="Ask a question about the lecture..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={!selectedLecture || loading}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleSend}
          disabled={!input.trim() || !selectedLecture || loading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage; 