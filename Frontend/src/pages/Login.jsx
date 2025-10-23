import React, { useState, useEffect } from "react";
import API from "../api/api";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogIn } from "lucide-react";

export default function Login() {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState("");
  const [role, setRole] = useState("teacher");
  const navigate = useNavigate();

  useEffect(() => {
    API.get("/users").then(res => setUsers(res.data)).catch(() => {});
  }, []);

  const handleLogin = async () => {
    if (!name.trim()) return alert("Please enter your name");
    let user = users.find(u => u.name === name && u.role === role);
    if (!user) {
      const res = await API.post("/users", { name, role });
      user = res.data;
    }
    navigate(`/dashboard/${user.id}`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-2xl p-10 w-[90%] max-w-md flex flex-col items-center"
      >
        <div className="flex items-center gap-2 mb-6">
          <LogIn className="text-indigo-600 w-7 h-7" />
          <h1 className="text-3xl font-bold text-gray-800">Welcome Back</h1>
        </div>

        <p className="text-gray-600 mb-8 text-center text-sm">
          Sign in to your classroom to continue
        </p>

        <div className="w-full flex flex-col gap-4">
          <input
            type="text"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />

          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all bg-white"
          >
            <option value="teacher">👨‍🏫 Teacher</option>
            <option value="student">🎓 Student</option>
          </select>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleLogin}
            className="bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-semibold shadow-md transition-all duration-300"
          >
            Enter
          </motion.button>
        </div>

        <p className="text-xs text-gray-500 mt-6">
          © 2025 Classroom Portal — Designed by <span className="font-semibold text-indigo-600">You 😎</span>
        </p>
      </motion.div>
    </div>
  );
}
