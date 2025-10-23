import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../api/api";
import { motion, AnimatePresence } from "framer-motion";
import { PlusCircle, BookOpen, ClipboardList, Send } from "lucide-react";

export default function ClassPage() {
  const { classId, userId } = useParams();
  const [cls, setCls] = useState({});
  const [notes, setNotes] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState("");
  const [user, setUser] = useState({});
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [assignmentTitle, setAssignmentTitle] = useState("");
  const [assignmentDesc, setAssignmentDesc] = useState("");

  useEffect(() => {
    API.get(`/users/${userId}`).then((res) => setUser(res.data));
    fetchClass();
    fetchNotes();
    fetchAssignments();
    fetchMessages();
  }, []);

  const fetchClass = () =>
    API.get(`/classes/${classId}`).then((res) => setCls(res.data));
  const fetchNotes = () =>
    API.get(`/classes/${classId}/notes`).then((res) => setNotes(res.data));
  const fetchAssignments = () =>
    API.get(`/classes/${classId}/assignments`).then((res) =>
      setAssignments(res.data)
    );
  const fetchMessages = () =>
    API.get(`/classes/${classId}/messages`).then((res) => setMessages(res.data));

  const addNote = async () => {
    if (!noteTitle || !noteContent) return;
    await API.post(`/classes/${classId}/notes`, {
      class_id: classId,
      title: noteTitle,
      content: noteContent,
    });
    setNoteTitle("");
    setNoteContent("");
    setShowNoteModal(false);
    fetchNotes();
  };

  const createAssignment = async () => {
    if (!assignmentTitle || !assignmentDesc) return;
    await API.post(`/classes/${classId}/assignments`, {
      class_id: classId,
      title: assignmentTitle,
      description: assignmentDesc,
    });
    setAssignmentTitle("");
    setAssignmentDesc("");
    setShowAssignModal(false);
    fetchAssignments();
  };

  const sendMessage = async () => {
    if (!messageText.trim()) return;
    await API.post(`/classes/${classId}/messages`, {
      class_id: classId,
      user_id: userId,
      content: messageText,
    });
    setMessageText("");
    fetchMessages();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex flex-col items-center py-10 px-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-5xl bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8"
      >
        {/* Header */}
        <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          {cls.name || "Classroom"}
        </h1>

        {/* Notes & Assignments */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Notes */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <BookOpen className="text-indigo-600" /> Notes
              </h2>
              {user.role === "teacher" && (
                <button
                  onClick={() => setShowNoteModal(true)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl flex items-center gap-1 text-sm font-semibold"
                >
                  <PlusCircle className="w-4 h-4" /> Add Note
                </button>
              )}
            </div>

            {notes.length === 0 ? (
              <p className="text-gray-500 italic">No notes yet.</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {notes.map((n) => (
                  <div
                    key={n.id}
                    className="border rounded-lg p-3 bg-gray-50 hover:bg-gray-100 transition"
                  >
                    <h3 className="font-semibold text-gray-800">{n.title}</h3>
                    <p className="text-gray-600 text-sm">{n.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Assignments */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <ClipboardList className="text-purple-600" /> Assignments
              </h2>
              {user.role === "teacher" && (
                <button
                  onClick={() => setShowAssignModal(true)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl flex items-center gap-1 text-sm font-semibold"
                >
                  <PlusCircle className="w-4 h-4" /> Add Assignment
                </button>
              )}
            </div>

            {assignments.length === 0 ? (
              <p className="text-gray-500 italic">No assignments yet.</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {assignments.map((a) => (
                  <Link
                    key={a.id}
                    to={`/class/${classId}/${userId}/assignments/${a.id}`}
                    className="block border rounded-lg p-3 bg-gray-50 hover:bg-gray-100 transition"
                  >
                    <h3 className="font-semibold text-gray-800">{a.title}</h3>
                    <p className="text-gray-600 text-sm">{a.description}</p>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="bg-white rounded-xl shadow-md p-6 h-[400px] flex flex-col">
          <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
            💬 Class Messages
          </h2>
          <div className="flex-1 overflow-y-auto space-y-2 mb-3 bg-gray-50 p-3 rounded-lg">
            {messages.length === 0 ? (
              <p className="text-gray-500 italic">No messages yet.</p>
            ) : (
              messages.map((m) => (
                <div
                  key={m.id}
                  className={`p-2 rounded-lg shadow-sm ${
                    m.user_id === userId
                      ? "bg-indigo-100 text-indigo-800 ml-auto max-w-[70%]"
                      : "bg-white text-gray-800 mr-auto max-w-[70%]"
                  }`}
                >
                  <span className="font-semibold">{m.user_id}</span>:{" "}
                  {m.content}
                </div>
              ))
            )}
          </div>
          <div className="flex">
            <input
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 p-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
            />
            <button
              onClick={sendMessage}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl ml-2 flex items-center gap-1"
            >
              <Send className="w-4 h-4" /> Send
            </button>
          </div>
        </div>
      </motion.div>

      {/* NOTE MODAL */}
      <AnimatePresence>
        {showNoteModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex justify-center items-center z-50"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
              className="bg-white rounded-2xl shadow-2xl p-8 w-[90%] max-w-md"
            >
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Add New Note
              </h3>
              <input
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
                placeholder="Note Title"
                className="w-full p-3 border rounded-xl mb-3"
              />
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="Note Description"
                rows={4}
                className="w-full p-3 border rounded-xl mb-4"
              />
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="px-4 py-2 rounded-xl bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={addNote}
                  className="px-4 py-2 rounded-xl bg-indigo-600 text-white"
                >
                  Add Note
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ASSIGNMENT MODAL */}
      <AnimatePresence>
        {showAssignModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex justify-center items-center z-50"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
              className="bg-white rounded-2xl shadow-2xl p-8 w-[90%] max-w-md"
            >
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Add New Assignment
              </h3>
              <input
                value={assignmentTitle}
                onChange={(e) => setAssignmentTitle(e.target.value)}
                placeholder="Assignment Title"
                className="w-full p-3 border rounded-xl mb-3"
              />
              <textarea
                value={assignmentDesc}
                onChange={(e) => setAssignmentDesc(e.target.value)}
                placeholder="Assignment Description"
                rows={4}
                className="w-full p-3 border rounded-xl mb-4"
              />
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2 rounded-xl bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={createAssignment}
                  className="px-4 py-2 rounded-xl bg-purple-600 text-white"
                >
                  Add Assignment
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
