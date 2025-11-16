// src/pages/Portal.jsx (NEW FILE)

import React from "react";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";

// Helper to map role names to dashboard paths
const roleDashboards = {
  owner: { name: "Owner", path: "/owner" },
  admin: { name: "Admin", path: "/admin/dashboard" },
  hod: { name: "HOD", path: "/hod-dashboard" },
  class_teacher: { name: "Class Teacher", path: "/teacher-dashboard" },
  teacher: { name: "Subject Teacher", path: "/teacher-dashboard" }, // Can go to same page
  student: { name: "Student", path: "/student-dashboard" },
};

export default function Portal() {
  const { currentUser } = useAuth();
  const roles = currentUser?.roles || [];

  // Filter the dashboards they are allowed to see
  const accessibleDashboards = roles
    .map(role => roleDashboards[role])
    .filter(Boolean); // Filter out any roles we don't have a dashboard for

  const buttonClass = "w-full text-left p-6 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg text-2xl font-bold";

  return (
    <Layout>
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">
          Welcome, {currentUser?.full_name}
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          You have multiple roles. Please select a dashboard to continue.
        </p>

        <div className="space-y-4">
          {accessibleDashboards.length > 0 ? (
            accessibleDashboards.map((dash) => (
              <Link key={dash.path} to={dash.path}>
                <button className={buttonClass}>
                  Go to {dash.name} Dashboard
                </button>
              </Link>
            ))
          ) : (
            <p className="dark:text-gray-300">You do not have any assigned roles.</p>
          )}
        </div>
      </div>
    </Layout>
  );
}