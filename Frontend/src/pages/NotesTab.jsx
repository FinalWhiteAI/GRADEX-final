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
    const fd = new FormData();
    fd.append("class_id", classId);
    fd.append("title", title);
    fd.append("file", file);

    await api.post("/api/notes/upload", fd, {
      // headers: { "Content-Type": "multipart/form-data" },
    });

    fetchNotes();
    setTitle("");
    setFile(null);
  } catch (err) {
    console.error(err);
    alert("Only teachers can upload notes");
  }
};

useEffect(() => {
  if (classId) fetchNotes();
}, [classId]);

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
            <a
        href={n.file_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-500 underline"
      >
        Open File
      </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
