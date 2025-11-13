import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useParams } from "react-router-dom";

export default function Submissions() {
  const { id } = useParams(); // assignment_id
  const [subs, setSubs] = useState([]);

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

  const grade = async (subId, marks) => {
    try {
      await api.post(`/api/submissions/${subId}/grade`, { marks }, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
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
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-4">Student Submissions</h1>

      {subs.length === 0 && <p>No submissions yet.</p>}

      {subs.map((s) => (
        <div
          key={s.id}
          className="bg-white dark:bg-gray-100 p-4 rounded-md shadow mb-4"
        >
          <p><strong>{s.student_name}</strong> ({s.student_email})</p>
          <p className="mt-2">{s.text_content || "No text provided"}</p>

          {s.file_path && (
            <a
              href={s.file_path}
              target="_blank"
              className="text-blue-500 underline mt-2 block"
            >
              Download File
            </a>
          )}

          <div className="mt-3 flex gap-2">
            <input
              placeholder="Marks"
              type="number"
              onChange={(e) => (s.tempMarks = e.target.value)}
              className="border px-2 py-1 rounded"
            />
            <button
              onClick={() => grade(s.id, s.tempMarks)}
              className="bg-green-600 text-white px-3 py-1 rounded-md"
            >
              Grade
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
