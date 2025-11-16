import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const roles = user.roles || [];
  const orgType = user.org_type || "school";

  const links = [
    { to: "/dashboard", label: "Dashboard" },
  ];

  if (roles.includes("owner"))
    links.push({ to: "/owner", label: "Manage Orgs" });

  if (roles.includes("admin")) {
    links.push({ to: "/admin/dashboard", label: "Admin Dashboard" });
    if (orgType !== "school") links.push({ to: "/departments", label: "Departments" });
    links.push({ to: "/import", label: "Import Users " });
  }

  if (roles.includes("class_teacher"))
    links.push({ to: "/teacher/dashboard", label: "Class Teacher" });

  if (roles.includes("sub_teacher"))
    links.push({ to: "/subteacher/dashboard", label: "Subject Teacher" });

  if (roles.includes("student"))
    links.push({ to: "/student/dashboard", label: "Student Dashboard" });
  if (roles.includes("hod"))
  links.push({ to: "/hod/dashboard", label: "HOD Dashboard" });

  return (
    <aside className="w-60 min-h-screen bg-gray-200 dark:bg-gray-800 text-black dark:text-white p-4">
      <div className="space-y-3">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              location.pathname === l.to
                ? "bg-blue-600 text-white"
                : "hover:bg-blue-100 dark:hover:bg-gray-700"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </div>
    </aside>
  );
}
