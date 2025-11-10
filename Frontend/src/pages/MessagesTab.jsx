import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function MessagesTab({ classId }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [isPublic, setIsPublic] = useState(true);

  const fetchMessages = async () => {
    const res = await api.get(`/api/classes/${classId}/messages`);
    setMessages(res.data || []);
  };

  const sendMessage = async () => {
    if (!text) return;
    try {
      await api.post("/api/messages", {
        class_id: classId,
        content: text,
        is_public: isPublic,
      });
      setText("");
      fetchMessages();
    } catch {
      alert("Error sending message");
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  return (
    <div>
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mb-4">
        <textarea
          placeholder="Type your message..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="border px-3 py-1 rounded-md w-full mb-2"
        />
        <div className="flex items-center gap-2 mb-2">
          <label className="text-sm">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={() => setIsPublic(!isPublic)}
            />{" "}
            Public
          </label>
        </div>
        <button
          onClick={sendMessage}
          className="bg-blue-600 text-white px-3 py-1 rounded-md"
        >
          Send
        </button>
      </div>

      <ul className="space-y-2">
        {messages.map((m) => (
          <li key={m.id} className="bg-white dark:bg-gray-800 p-3 rounded-md shadow">
            <p className="text-sm text-gray-500">
              {m.is_public ? "Public" : "Private"} message
            </p>
            <p>{m.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
