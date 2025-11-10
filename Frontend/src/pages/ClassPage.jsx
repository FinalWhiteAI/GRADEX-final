import React, { useState } from "react";
import { useParams } from "react-router-dom";
import Layout from "../components/Layout";
import AssignmentsTab from "./AssignmentsTab";
import NotesTab from "./NotesTab";
import MessagesTab from "./MessagesTab";
import GradesTab from "./GradesTab";

export default function ClassPage() {
  const { id } = useParams();
  const [tab, setTab] = useState("assignments");

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Classroom</h1>

      <div className="flex gap-2 mb-4">
        {["assignments", "notes", "messages", "grades"].map((t) => (
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

      {tab === "assignments" && <AssignmentsTab classId={id} />}
      {tab === "notes" && <NotesTab classId={id} />}
      {tab === "messages" && <MessagesTab classId={id} />}
      {tab === "grades" && <GradesTab classId={id} />}
    </Layout>
  );
}
