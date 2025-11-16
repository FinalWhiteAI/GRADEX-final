import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function GradesTab({ classId }) {
  const { user } = useAuth();

  const [classInfo, setClassInfo] = useState(null);
  const [grades, setGrades] = useState([]);
  const [students, setStudents] = useState([]);

  const [form, setForm] = useState({
    student_id: "",
    unit_name: "",
    marks: "",
  });

  // Fetch class info to get classname as subject
  const fetchClassInfo = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}`);
      setClassInfo(res.data);
    } catch (err) {
      console.error("Class info error", err);
    }
  };

  // Fetch students
  const fetchStudents = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}/students`);
      const uniq = [];
      const seen = new Set();

      for (const s of res.data || []) {
        if (!seen.has(s.id)) {
          uniq.push(s);
          seen.add(s.id);
        }
      }
      setStudents(uniq);
    } catch (err) {
      console.error("Student fetch error", err);
    }
  };

  // Fetch grades only for this class
  const fetchGrades = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}/grades`);
      setGrades(res.data || []);
    } catch (err) {
      console.error("Grades fetch error:", err);
    }
  };

  const uploadGrade = async () => {
    if (!form.student_id || !form.unit_name || !form.marks)
      return alert("Fill all fields");

   
    try {
      const me = await api.get("/api/users/me");

      await api.post("/api/finalmarks", {
        org_id: me.data.org_id,
        class_id: classId,
        student_id: form.student_id,
        subject_name: classInfo.title, // 👈 subject = class title
        unit_name: form.unit_name,
        marks: form.marks,
      });

      fetchGrades();
      setForm({ student_id: "", unit_name: "", marks: "" });
    } catch (err) {
      console.error(err);
      
      alert("Only teachers can upload marks");
    }
  };

  useEffect(() => {
    fetchClassInfo();
    fetchStudents();
    fetchGrades();
  }, []);

  const canUpload = user?.roles?.includes("sub_teacher");

  // Group by subject name
  const grouped = grades.reduce((acc, g) => {
    if (!acc[g.subject_name]) acc[g.subject_name] = [];
    acc[g.subject_name].push(g);
    return acc;
  }, {});

  return (
    <div>
      {/* Teacher Upload Section */}
      {canUpload && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
          <h2 className="font-medium mb-2">
            Upload Final Mark (Subject: {classInfo?.title})
          </h2>

          {/* Student Dropdown */}
          <select
            value={form.student_id}
            onChange={(e) => setForm({ ...form, student_id: e.target.value })}
            className="border px-3 py-1 rounded-md mb-2 text-blue-500"
          >
            <option value="">Select Student</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.full_name} ({s.email})
              </option>
            ))}
          </select>

          <input
            placeholder="Unit"
            value={form.unit_name}
            onChange={(e) =>
              setForm({ ...form, unit_name: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-2"
          />

          <input
            placeholder="Marks"
            type="number"
            value={form.marks}
            onChange={(e) =>
              setForm({ ...form, marks: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-3"
          />

          <button
            onClick={uploadGrade}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Upload
          </button>
        </div>
      )}

      {/* Student View - only own marks */}
      {user.roles.includes("student") &&
        Object.keys(grouped).map((subject) => (
          <div
            key={subject}
            className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-4"
          >
            <h3 className="text-lg font-bold mb-2">{subject}</h3>

            {grouped[subject]
              .filter((g) => g.student_id === user.id)
              .map((g) => (
                <p key={g.id} className="text-gray-300">
                  <strong>{g.unit_name}</strong>: {g.marks} marks
                </p>
              ))}
          </div>
        ))}

      {/* Teacher View - All marks */}
      {(user.roles.includes("sub_teacher") ||
        user.roles.includes("class_teacher") ||
        user.roles.includes("admin")) &&
        Object.keys(grouped).map((subject) => (
          <div
            key={subject}
            className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-4"
          >
            <h3 className="text-lg font-bold mb-2">{subject}</h3>

            {grouped[subject].map((g) => (
              <p key={g.id} className="text-gray-300">
                <strong>{g.unit_name}</strong>: {g.marks} marks (Student:{" "}
                {g.student_id})
              </p>
            ))}
          </div>
        ))}

      {grades.length === 0 && <p>No grades yet.</p>}
    </div>
  );
}
