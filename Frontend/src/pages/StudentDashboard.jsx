

import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function StudentDashboard() {
  const [classes, setClasses] = useState([]);
 
  const [code, setCode] = useState("");
  const navigate = useNavigate();

  const fetchMyClasses = async () => {
    try {
      const res = await api.get("/api/classes", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      setClasses(res.data || []);
    } catch (err) {
      console.error("Fetch my classes err", err);
      setClasses([]);
    }
  };
  const joinClass = async () => {
    if (!code) return alert("Enter class code");
    try {
      await api.post("/api/classes/join", { class_code: code });
      alert("Joined successfully!");
     await fetchMyClasses();
      setCode("");
    } catch {
      alert("Invalid class code");
    }
  };


  useEffect(() => {
    fetchMyClasses();
  }, []);

  return (
    <Layout>
       <div className="bg-white dark:bg-gray-800 p-4 rounded-md mb-6 shadow">
        <h2 className="font-medium mb-2">Join a Class</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Enter Class Code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="border px-3 py-1 rounded-md"
          />
          <button
            onClick={joinClass}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Join
          </button>
        </div>
      </div>
      <h1 className="text-2xl font-semibold mb-4">My Classes</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {classes.length === 0 && <p>No classes yet.</p>}
        {classes.map((c) => (
          <div key={c.id} className="bg-white dark:bg-gray-800 p-4 rounded-md shadow">
            <h2 className="text-lg font-semibold">{c.title}</h2>
            <p className="text-sm text-gray-500">{c.description}</p>
            <button className="mt-2 bg-blue-600 text-white px-3 py-1 rounded-md"
                    onClick={() => navigate(`/class/${c.id}`)}>
              Open Class
            </button>
          </div>
        ))}
      </div>
    </Layout>
  );
}
