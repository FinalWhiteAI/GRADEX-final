import React from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div className="flex min-h-screen ">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Navbar />
        <main className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}
