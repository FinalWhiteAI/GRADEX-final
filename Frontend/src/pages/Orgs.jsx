import { useState, useEffect } from "react";
import api from "../api/axios";
import Navbar from "../components/Navbar";

export default function Orgs() {
  const [orgs, setOrgs] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("school");

  async function fetchOrgs() {
    const res = await api.get("/api/orgs");
    setOrgs(res.data);
  }

  async function createOrg() {
    try {
      await api.post("/api/orgs", { name, org_type: type });
      setName("");
      fetchOrgs();
    } catch (err) {
      alert(err.response?.data?.detail);
    }
  }

  useEffect(() => {
    fetchOrgs();
  }, []);

  return (
    <>
      <Navbar />
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-3">Organizations</h2>
        <div className="flex gap-3 mb-5">
          <input
            placeholder="Org Name"
            className="border p-2 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <select
            className="border p-2 rounded"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <option value="school">School</option>
            <option value="college">College</option>
            <option value="university">University</option>
          </select>
          <button onClick={createOrg} className="bg-indigo-600 text-white px-4 py-2 rounded">
            Create
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {orgs.map((o) => (
            <div key={o.id} className="bg-white p-4 rounded shadow">
              <h3 className="font-bold text-indigo-600">{o.name}</h3>
              <p className="text-gray-500">{o.org_type}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
