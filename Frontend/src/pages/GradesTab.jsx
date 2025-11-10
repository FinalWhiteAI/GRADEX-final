import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function GradesTab({ classId }) {
  const { user } = useAuth();
  const [grades, setGrades] = useState([]);
  const [form, setForm] = useState({
    student_id: "",
    subject_name: "",
    unit_name: "",
    marks: "",
  });

  const fetchGrades = async () => {
    const me = await api.get("/api/users/me");
    const orgId = me.data.org_id;
    const res = await api.get(`/api/orgs/${orgId}/grades`);
    setGrades(res.data || []);
  };

  const uploadGrade = async () => {
    try {
      const me = await api.get("/api/users/me");
      await api.post("/api/finalmarks", {
        org_id: me.data.org_id,
        class_id: classId,
        ...form,
      });
      fetchGrades();
      setForm({ student_id: "", subject_name: "", unit_name: "", marks: "" });
    } catch {
      alert("Only teachers can upload marks");
    }
  };

  useEffect(() => {
    fetchGrades();
  }, []);

  const canUpload = user?.roles?.includes("sub_teacher");

  return (
    <div>
      {canUpload && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
          <h2 className="font-medium mb-2">Upload Final Mark</h2>
          <div className="grid gap-2">
            <input
              placeholder="Student ID"
              value={form.student_id}
              onChange={(e) =>
                setForm({ ...form, student_id: e.target.value })
              }
              className="border px-3 py-1 rounded-md"
            />
            <input
              placeholder="Subject"
              value={form.subject_name}
              onChange={(e) =>
                setForm({ ...form, subject_name: e.target.value })
              }
              className="border px-3 py-1 rounded-md"
            />
            <input
              placeholder="Unit"
              value={form.unit_name}
              onChange={(e) => setForm({ ...form, unit_name: e.target.value })}
              className="border px-3 py-1 rounded-md"
            />
            <input
              placeholder="Marks"
              type="number"
              value={form.marks}
              onChange={(e) => setForm({ ...form, marks: e.target.value })}
              className="border px-3 py-1 rounded-md"
            />
            <button
              onClick={uploadGrade}
              className="bg-blue-600 text-white px-3 py-1 rounded-md"
            >
              Upload
            </button>
          </div>
        </div>
      )}

      <h2 className="text-xl font-semibold mb-3">Final Marks</h2>
      <ul className="space-y-2">
        {grades.map((g) => (
          <li key={g.id} className="bg-white dark:bg-gray-800 p-3 rounded-md shadow">
            <p><strong>{g.subject_name}</strong> ({g.unit_name}) - {g.marks} marks</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
