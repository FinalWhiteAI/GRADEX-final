import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function TeacherDashboard() {
  const [classes, setClasses] = useState([]);
  const [newSubTeacher, setNewSubTeacher] = useState({
    email: "",
    full_name: "",
  });

  const fetchClasses = async () => {
    const res = await api.get("/api/classes");
    setClasses(res.data || []);
  };

  const addSubTeacher = async () => {
    if (!newSubTeacher.email) return alert("Enter sub-teacher email");
    try {
      await api.post("/api/teachers/add-sub", newSubTeacher);
      alert("Sub teacher added");
      setNewSubTeacher({ email: "", full_name: "" });
    } catch {
      alert("Failed to add sub-teacher");
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Class Teacher Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {classes.map((cls) => (
          <div key={cls.id} className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
            <h2 className="text-lg font-semibold">{cls.title}</h2>
            <p>{cls.description}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Code: {cls.class_code}</p>
          </div>
        ))}
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mt-6 shadow">
        <h2 className="font-medium mb-2">Add Subject Teacher</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name"
            className="border px-3 py-1 rounded-md"
            value={newSubTeacher.full_name}
            onChange={(e) =>
              setNewSubTeacher({ ...newSubTeacher, full_name: e.target.value })
            }
          />
          <input
            type="email"
            placeholder="Email"
            className="border px-3 py-1 rounded-md"
            value={newSubTeacher.email}
            onChange={(e) =>
              setNewSubTeacher({ ...newSubTeacher, email: e.target.value })
            }
          />
          <button
            onClick={addSubTeacher}
            className="bg-green-600 text-white px-3 py-1 rounded-md"
          >
            Add Sub Teacher
          </button>
        </div>
      </div>
    </Layout>
  );
}
