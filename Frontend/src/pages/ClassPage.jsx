

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Layout from "../components/Layout";
import AssignmentsTab from "./AssignmentsTab";
import NotesTab from "./NotesTab";
import MessagesTab from "./MessagesTab";
import GradesTab from "./GradesTab";
import api from "../api/axios";

export default function ClassPage() {
  const { id } = useParams();
  const [tab, setTab] = useState("assignments");
  const [role, setRole] = useState("");

  // Fetch user's role from backend
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get("/api/users/me", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        });
        const roles = JSON.parse(res.data.roles || "[]");
        setRole(roles[0]); // assume single role for simplicity
      } catch (err) {
        console.error("Role fetch error: ", err);
      }
    };
    fetchUser();
  }, []);

  // Role-Based Visible Tabs
  const tabs = {
    student: ["assignments", "notes", "messages","grades"],
    sub_teacher: ["assignments", "notes", "messages", "grades"],
    class_teacher: ["grades"],
    admin: ["grades"],
    hod: ["grades"],
  };

  const allowedTabs = tabs[role] || [];

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Classroom</h1>

      {/* TAB BUTTONS */}
      <div className="flex gap-2 mb-4">
        {allowedTabs.map((t) => (
          <button
            key={t}
            className={`px-3 py-1 rounded-md ${
              tab === t ? "bg-blue-600 text-white" : "bg-gray-200 dark:bg-gray-700"
            }`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}
      {tab === "assignments" && <AssignmentsTab classId={id} role={role} />}
      {tab === "notes" && <NotesTab classId={id} role={role} />}
      {tab === "messages" && <MessagesTab classId={id} role={role} />}
      {tab === "grades" && <GradesTab classId={id} role={role} />}
    </Layout>
  );
}
