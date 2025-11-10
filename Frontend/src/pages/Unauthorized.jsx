import React from "react";
import { Link } from "react-router-dom";

export default function Unauthorized() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-900">
      <h1 className="text-4xl font-bold text-red-600 mb-2">403 - Unauthorized</h1>
      <p className="mb-4">You don’t have permission to access this page.</p>
      <Link to="/" className="text-blue-600 hover:underline">
        Go to Login
      </Link>
    </div>
  );
}
