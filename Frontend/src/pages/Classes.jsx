import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function Classes() {
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
      await api.post("/api/classes", {
        ...newClass,
        org_id: me.data.org_id,
      });
      fetchClasses();
      setNewClass({ title: "", description: "" });
    } catch {
      alert("Failed to create class");
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">My Classes</h1>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mb-6 shadow">
        <h2 className="font-medium mb-2">Create Class</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Class Title"
            className="border px-3 py-1 rounded-md"
            value={newClass.title}
            onChange={(e) =>
              setNewClass({ ...newClass, title: e.target.value })
            }
          />
          <textarea
            placeholder="Description"
            className="border px-3 py-1 rounded-md"
            value={newClass.description}
            onChange={(e) =>
              setNewClass({ ...newClass, description: e.target.value })
            }
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
          <div
            key={cls.id}
            className="bg-white dark:bg-gray-800 p-4 rounded-md shadow cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => (window.location.href = `/class/${cls.id}`)}
          >
            <h2 className="font-medium">Title: {cls.title}</h2>
            <p className="text-sm">Description: {cls.description}</p>
            <p className="text-xs text-gray-500">Code: {cls.class_code}</p>
          </div>
        ))}
      </div>
    </Layout>
  );
}
