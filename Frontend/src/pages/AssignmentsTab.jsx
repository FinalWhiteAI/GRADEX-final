import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function AssignmentsTab({ classId }) {
  const [assignments, setAssignments] = useState([]);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const { user } = useAuth();

  const fetchAssignments = async () => {
    const res = await api.get(`/api/classes/${classId}/assignments`);
    setAssignments(res.data || []);
  };

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

  useEffect(() => {
    fetchAssignments();
  }, []);

  const isSubTeacher = user?.roles?.includes("sub_teacher");

  return (
    <div>
      {isSubTeacher && (
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

      <h2 className="text-xl font-semibold mb-3">Assignments</h2>
      <ul className="space-y-2">
        {assignments.map((a) => (
          <li key={a.id} className="bg-white dark:bg-gray-800 p-3 rounded-md shadow">
            <h3 className="font-medium">{a.title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{a.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
