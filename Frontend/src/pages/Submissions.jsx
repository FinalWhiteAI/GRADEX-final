import { useState } from "react";
import api from "../api/axios";
import Navbar from "../components/Navbar";

export default function Submissions() {
  const [assignmentId, setAssignmentId] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [grade, setGrade] = useState("");

  async function submitWork() {
    const form = new FormData();
    form.append("file", file);
    form.append("payload", JSON.stringify({ assignment_id: assignmentId, text_content: text }));
    await api.post("/api/submissions", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    alert("Submitted!");
  }

  async function loadSubs() {
    const res = await api.get(`/api/assignments/${assignmentId}/submissions`);
    setSubmissions(res.data);
  }

  async function gradeSubmission(id) {
    await api.post(`/api/submissions/${id}/grade`, grade);
    alert("Graded!");
    loadSubs();
  }

  return (
    <>
      <Navbar />
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-3">Submissions</h2>
        <div className="flex gap-3 mb-5">
          <input
            placeholder="Assignment ID"
            className="border p-2 rounded"
            value={assignmentId}
            onChange={(e) => setAssignmentId(e.target.value)}
          />
          <button onClick={loadSubs} className="bg-gray-200 px-3 py-1 rounded">
            Load
          </button>
        </div>

        <textarea
          placeholder="Your text answer"
          className="border w-full p-2 mb-2 rounded"
          value={text}
          onChange={(e) => setText(e.target.value)}
        ></textarea>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} className="mb-3" />
        <button onClick={submitWork} className="bg-indigo-600 text-white px-4 py-2 rounded">
          Submit
        </button>

        <h3 className="mt-6 font-semibold">Submitted:</h3>
        <ul>
          {submissions.map((s) => (
            <li key={s.id} className="border-b py-2">
              <p>{s.student_id}</p>
              <p>Grade: {s.grade ?? "Not graded"}</p>
              {s.file_path && (
                <a href={s.file_path} className="text-blue-600 text-sm underline" target="_blank">
                  File
                </a>
              )}
              <input
                type="number"
                placeholder="Grade"
                className="border p-1 ml-2 w-16 rounded"
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
              />
              <button
                onClick={() => gradeSubmission(s.id)}
                className="ml-2 bg-green-500 text-white px-2 py-1 rounded"
              >
                Grade
              </button>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
