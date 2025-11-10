import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function NotesTab({ classId }) {
  const { user } = useAuth();
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);

  const fetchNotes = async () => {
    const res = await api.get(`/api/classes/${classId}/notes`);
    setNotes(res.data || []);
  };

  const uploadNote = async () => {
    if (!file || !title) return alert("Fill all fields");
    try {
      await api.post("/api/notes", {
        class_id: classId,
        title,
        file_path: `notes/${file.name}`,
      });
      fetchNotes();
      setTitle("");
      setFile(null);
    } catch {
      alert("Only teachers can upload notes");
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const canUpload = user?.roles?.includes("sub_teacher") || user?.roles?.includes("class_teacher");

  return (
    <div>
      {canUpload && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
          <h2 className="font-medium mb-2">Upload Note</h2>
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="border px-3 py-1 rounded-md w-full mb-2"
          />
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="border px-3 py-1 rounded-md w-full mb-2"
          />
          <button
            onClick={uploadNote}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Upload
          </button>
        </div>
      )}

      <h2 className="text-xl font-semibold mb-3">Notes</h2>
      <ul className="space-y-2">
        {notes.map((n) => (
          <li key={n.id} className="bg-white dark:bg-gray-800 p-3 rounded-md shadow">
            <h3 className="font-medium">{n.title}</h3>
            <p className="text-sm text-gray-500">{n.file_path}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
