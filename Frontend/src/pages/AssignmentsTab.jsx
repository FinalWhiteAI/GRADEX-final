

import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function AssignmentsTab({ classId, role }) {
  const [assignments, setAssignments] = useState([]);
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const navigate=useNavigate()  
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");

  const fetchAssignments = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}/assignments`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      setAssignments(res.data || []);
    } catch (err) {
      console.error("Assignment fetch error:", err);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);
   const createAssignment = async () => {
    try {
      await api.post("/api/assignments", {
        class_id: classId,
        title,
        description: desc,
        assignment_type: "file",
      });
      fetchAssignments();
      setTitle("");
      setDesc("");
    } catch {
      alert("You must be a subject teacher to create assignments.");
    }
  };

  const submitAssignment = async (assignmentId) => {
  if (!text && !file) {
    alert("Please write something or upload a file");
    return;
  }

  const formData = new FormData();
  formData.append("assignment_id", assignmentId);   // REQUIRED
  if (file) formData.append("file", file);
  if (text) formData.append("text_content", text);

  try {
    await api.post("/api/submissions", formData, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "multipart/form-data",
      },
    });
    alert("Submitted!");
    setFile("");
    setText("")
    
  } catch (err) {
    console.error("Submit error:", err);
    alert("Submission failed");
  }
};


  return (
    <div>
      {role === "sub_teacher" && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
          <h2 className="font-medium mb-2">Create Assignment</h2>
          <input
            type="text"
            placeholder="Title"
            className="border px-3 py-1 rounded-md w-full mb-2"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            placeholder="Description"
            className="border px-3 py-1 rounded-md w-full mb-2"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
          />
          <button
            onClick={createAssignment}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Create
          </button>
        </div>
      )}
      {/* ASSIGNMENT LIST */}
      {assignments.map((a) => (
        <div key={a.id} className="bg-white dark:bg-gray-800 p-4 rounded-md mt-4 shadow">
          <h2 className="text-lg font-bold">Title: {a.title}</h2>
          <p className="text-sm text-gray-400">Description: {a.description}</p>

          {/* STUDENT SUBMISSION UI */}
          {role === "student" && (
            <div className="mt-3 border-t pt-3">
              <h3 className="font-medium mb-2">Submit Assignment</h3>

              <textarea
                className="border w-full p-2 rounded-md"
                placeholder="Write text (optional)"
                value={text}
                onChange={(e) => setText(e.target.value)}
              ></textarea>

              <input
                type="file"
                className="mt-2"
                onChange={(e) => setFile(e.target.files[0])}
              />

              <button
                onClick={() => submitAssignment(a.id)}
                className="mt-3 bg-green-600 text-white px-3 py-1 rounded-md"
              >
                Submit
              </button>
            </div>
          )}

          {/* SUB TEACHER CAN SEE SUBMISSIONS */}
          {role === "sub_teacher" && (

            <button
              onClick={() => navigate(`/assignment/${a.id}/submissions`)}
              className="mt-3 bg-blue-600 text-white px-3 py-1 rounded-md"
            >
              View Submissions
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
