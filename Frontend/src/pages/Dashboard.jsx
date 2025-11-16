
import React from "react";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();

  if (!user) return null;

  // ✅ Fix: ensure roles is always an array
  let roles = [];
  try {
    if (Array.isArray(user.roles)) {
      roles = user.roles;
    } else if (typeof user.roles === "string") {
      roles = JSON.parse(user.roles);
    }
  } catch (e) {
    roles = [];
  }

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">
        Welcome, {user.full_name || user.email}
      </h1>

      <div className="bg-white dark:bg-gray-800 shadow rounded-md p-4">
        <h2 className="text-lg font-medium mb-2">Your Details</h2>
        <p><strong>Email:</strong> {user.email}</p>
       
        <p><strong>Roles:</strong> {roles.join(", ") || "N/A"}</p>
       
      </div>
    </Layout>
  );
}
