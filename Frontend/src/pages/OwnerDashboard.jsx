import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function OwnerDashboard() {
  const [orgs, setOrgs] = useState([]);
  const [newOrg, setNewOrg] = useState({ name: "", org_type: "school" });
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [orgId, setOrgId] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");

  const fetchOrgs = async () => {
    const res = await api.get("/api/orgs");
    setOrgs(res.data);
  };

  const createOrg = async () => {
    if (!newOrg.name) return alert("Enter org name");
    setLoading(true);
    try {
      await api.post("/api/orgs", newOrg);
      fetchOrgs();
      setNewOrg({ name: "", org_type: "school" });
    } finally {
      setLoading(false);
    }
  };

  const createAdmin = async () => {
    if (!orgId || !email) return alert("Enter all fields");
    setLoading(true);
    try {
      await api.post(`/api/orgs/${orgId}/admin/create`, {
        email,
        full_name: fullName,
        password

      });
      alert("Admin created");
      setEmail("");
      setFullName("");
      setOrgId("");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrgs();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Owner Dashboard</h1>

      {/* Org creation */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mb-6 shadow">
        <h2 className="font-medium mb-2">Create Organization</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Organization Name"
            value={newOrg.name}
            onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
            className="border px-3 py-1 rounded-md"
          />
          <select
            value={newOrg.org_type}
            onChange={(e) => setNewOrg({ ...newOrg, org_type: e.target.value })}
            className="border px-3 py-1 rounded-md"
          >
            <option value="school">School</option>
            <option value="college">College</option>
            <option value="university">University</option>
          </select>
          <button
            onClick={createOrg}
            disabled={loading}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            {loading ? "Creating..." : "Create"}
          </button>
        </div>
      </div>

      {/* Org list */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
        <h2 className="font-medium mb-2">Organizations</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Name</th>
              <th>Type</th>
              <th>ID</th>
            </tr>
          </thead>
          <tbody>
            {orgs.map((o) => (
              <tr key={o.id} className="border-b">
                <td className="py-2">{o.name}</td>
                <td>{o.org_type}</td>
                <td>{o.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create admin */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mt-6 shadow">
        <h2 className="font-medium mb-2">Create Admin</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name"
            className="border px-3 py-1 rounded-md"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
          <input
            type="email"
            placeholder="Admin Email"
            className="border px-3 py-1 rounded-md"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
        type="password"
        placeholder="Password (optional)"
        className="w-full p-2 mb-3 border rounded"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
          <select
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="border px-3 py-1 rounded-md"
          >
            <option value="">Select Organization</option>
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
          <button
            onClick={createAdmin}
            className="bg-green-600 text-white px-3 py-1 rounded-md"
          >
            Create Admin
          </button>
        </div>
      </div>
    </Layout>
  );
}
