import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchDepartments = async () => {
    try {
      const me = await api.get("/api/users/me");
      const res = await api.get(`/api/orgs/${me.data.org_id}/departments`);
      setDepartments(res.data || []);
    } catch {
      setDepartments([]);
    }
  };

  const createDepartment = async () => {
    if (!name) return alert("Enter department name");
    setLoading(true);
    try {
      const me = await api.get("/api/users/me");
      await api.post("/api/departments/create", {
        org_id: me.data.org_id,
        name,
      });
      setName("");
      fetchDepartments();
    } catch {
      alert("Failed to create department");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDepartments();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Departments</h1>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mb-6 shadow">
        <h2 className="font-medium mb-2">Add Department</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Department Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border px-3 py-1 rounded-md flex-1"
          />
          <button
            onClick={createDepartment}
            disabled={loading}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            {loading ? "Adding..." : "Add"}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
        <h2 className="font-medium mb-2">Existing Departments</h2>
        {departments.length === 0 ? (
          <p className="text-sm text-gray-500">No departments yet.</p>
        ) : (
          <ul className="space-y-2">
            {departments.map((d) => (
              <li
                key={d.id}
                className="bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-md"
              >
                {d.name}
              </li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  );
}
