import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function SubTeacherDashboard() {
  const [classes, setClasses] = useState([]);
  const [newClass, setNewClass] = useState({ title: "", description: "" });

  const fetchClasses = async () => {
    const res = await api.get("/api/classes");
    setClasses(res.data || []);
  };

  const createClass = async () => {
    if (!newClass.title) return alert("Enter class title");
    try {
      const me = await api.get("/api/users/me");
      await api.post("/api/classes", { ...newClass, org_id: me.data.org_id });
      fetchClasses();
      setNewClass({ title: "", description: "" });
    } catch {
      alert("Error creating class");
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Subject Teacher Dashboard</h1>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
        <h2 className="font-medium mb-2">Create Class</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Class Title"
            value={newClass.title}
            onChange={(e) => setNewClass({ ...newClass, title: e.target.value })}
            className="border px-3 py-1 rounded-md"
          />
          <textarea
            placeholder="Description"
            value={newClass.description}
            onChange={(e) =>
              setNewClass({ ...newClass, description: e.target.value })
            }
            className="border px-3 py-1 rounded-md"
          />
          <button
            onClick={createClass}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Create
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {classes.map((cls) => (
          <div key={cls.id} className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
            <h2 className="font-medium">{cls.title}</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">{cls.description}</p>
          </div>
        ))}
      </div>
    </Layout>
  );
}
