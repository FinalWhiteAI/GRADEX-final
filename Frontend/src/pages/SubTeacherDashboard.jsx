import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function SubTeacherDashboard() {
  const [classes, setClasses] = useState([]);
  const [newClass, setNewClass] = useState({ title: "", description: "" });
  const navigate=useNavigate()

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

     {/* Show Existing Classes */}
      <div className="grid md:grid-cols-2 gap-4">
        {classes.length === 0 && <p>No classes yet.</p>}
        {classes.map((cls) => (
          <div
            key={cls.id}
            className="bg-white dark:bg-gray-800 p-4 rounded-md shadow flex flex-col justify-between"
          >
            <div>
              <h2 className="font-medium">{cls.title}</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {cls.description}
              </p>
              <p className="text-xs mt-1 text-gray-400">Code: {cls.class_code}</p>
            </div>

            <div className="mt-3 flex justify-end">
              <button
                onClick={() => navigate(`/class/${cls.id}`)}
                className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md"
              >
                View Class
              </button>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
