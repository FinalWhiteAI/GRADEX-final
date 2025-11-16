import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useParams } from "react-router-dom";

export default function Submissions() {
  const { id } = useParams(); // assignment_id
  const [subs, setSubs] = useState([]);
  const [marksInput, setMarksInput] = useState({});

  const fetchSubs = async () => {
    try {
      const res = await api.get(`/api/assignments/${id}/submissions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      setSubs(res.data || []);
    } catch (err) {
      console.log("Error fetching submissions", err);
    }
  };

  const grade = async (subId) => {
    const marks = marksInput[subId];
    if (!marks) return alert("Enter marks");

    try {
     await api.post(`/api/submissions/${subId}/grade`, { grade: Number(marks) }, {
  headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
});

      fetchSubs();
      alert("Graded!");
    } catch (err) {
      alert("Grade failed");
    }
  };

  useEffect(() => {
    fetchSubs();
  }, []);

  return (
    <div className="w-full min-h-screen bg-gray-900 text-gray-200 p-6">

      {/* Page Title */}
      <h1 className="text-2xl font-semibold mb-6">📚 Student Submissions</h1>

      {subs.length === 0 && (
        <p className="text-gray-400">No submissions yet.</p>
      )}

      {/* Submissions list */}
      <div className="space-y-5">
        {subs.map((s) => (
          <div
            key={s.id}
            className="bg-gray-800 border border-gray-700 p-5 rounded-xl shadow-lg"
          >
            {/* Student Name + Email */}
            <p className="text-lg font-semibold">
              {s.student_name}{" "}
              <span className="text-sm text-gray-400">
                ({s.student_email})
              </span>
            </p>

            {/* Text content */}
            <p className="mt-3 text-gray-300">
              {s.text_content || "No text provided"}
            </p>

            {/* File link */}
            {s.file_path && (
              <a
                href={s.file_path}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 underline mt-3 inline-block hover:text-blue-300"
              >
               Open File
              </a>
            )}

            {/* Grade Section */}
            <div className="mt-5 flex gap-3 items-center">
              <input
                type="number"
                placeholder="Marks"
                value={marksInput[s.id] || ""}
                onChange={(e) =>
                  setMarksInput({ ...marksInput, [s.id]: e.target.value })
                }
                className="w-32 px-3 py-2 rounded-lg bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              <button
                onClick={() => grade(s.id)}
                className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium transition"
              >
                Grade
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
