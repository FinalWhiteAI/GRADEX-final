import React from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="flex justify-between items-center px-6 py-3 shadow-md bg-gray-100 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-semibold">
        Classroom Portal
      </h1>
      {user && (
        <div className="flex items-center gap-3">
          <span className="text-sm">
            {user.full_name || user.email}
          </span>
          <button
            onClick={logout}
            className="bg-red-600 text-white px-3 py-1 rounded-md text-sm hover:bg-red-700 transition"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}
