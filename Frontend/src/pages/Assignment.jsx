import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import API from "../api/api";

export default function AssignmentPage() {
  const { classId, userId, assignmentId } = useParams();
  const [user, setUser] = useState({});
  const [submissions, setSubmissions] = useState([]);
  const [content, setContent] = useState("");

  useEffect(() => {
    API.get(`/users/${userId}`).then(res => setUser(res.data));
    fetchSubmissions();
  }, []);

  const fetchSubmissions = () => {
    API.get(`/assignments/${assignmentId}/submissions`).then(res => setSubmissions(res.data));
  };

  const submitAssignment = async () => {
    if (!content) return;
    await API.post(`/assignments/${assignmentId}/submit`, { student_id: userId,assignment_id:assignmentId, content });
    setContent("");
    fetchSubmissions();
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Assignment Page</h1>

      {user.role === "student" && (
        <div className="mb-4">
          <textarea value={content} onChange={e=>setContent(e.target.value)} className="border p-2 w-full" placeholder="Your submission"></textarea>
          <button onClick={submitAssignment} className="bg-blue-500 text-white px-4 py-2 rounded mt-2">Submit</button>
        </div>
      )}

      <h2 className="text-xl font-bold">Submissions</h2>
      {submissions.map(s => (
        <div key={s.id} className="border p-2 my-1 rounded">
          <p><strong>{s.student_id}</strong>: {s.content}</p>
        </div>
      ))}
    </div>
  );
}
