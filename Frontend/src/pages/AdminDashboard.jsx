import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function AdminDashboard() {
  const [teachers, setTeachers] = useState([]);
  const [newTeacher, setNewTeacher] = useState({ email: "", full_name: "" });

  const fetchTeachers = async () => {
    try {
      const res = await api.get("/api/users/me");
      const orgId = res.data.org_id;
      const r = await api.get(`/api/orgs/${orgId}/departments`);
      setTeachers(r.data || []);
    } catch {
      setTeachers([]);
    }
  };

  const createTeacher = async () => {
    if (!newTeacher.email) return alert("Enter teacher email");
    try {
      const me = await api.get("/api/users/me");
      await api.post(`/api/orgs/${me.data.org_id}/teachers/create`, newTeacher);
      alert("Class teacher added!");
      setNewTeacher({ email: "", full_name: "" });
      fetchTeachers();
    } catch (e) {
      alert("Error adding teacher");
    }
  };

  useEffect(() => {
    fetchTeachers();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Admin Dashboard</h1>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
        <h2 className="font-medium mb-2">Add Class Teacher</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name"
            value={newTeacher.full_name}
            onChange={(e) =>
              setNewTeacher({ ...newTeacher, full_name: e.target.value })
            }
            className="border px-3 py-1 rounded-md"
          />
          <input
            type="email"
            placeholder="Email"
            value={newTeacher.email}
            onChange={(e) =>
              setNewTeacher({ ...newTeacher, email: e.target.value })
            }
            className="border px-3 py-1 rounded-md"
          />
          <button
            onClick={createTeacher}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Create
          </button>
        </div>
      </div>
    </Layout>
  );
}
