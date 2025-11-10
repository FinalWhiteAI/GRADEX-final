// // import React, { useState, useEffect } from "react";
// // import { useParams, Link } from "react-router-dom";
// // import API from "../api/api";
// // import { motion } from "framer-motion";
// // import { PlusCircle, LogOut, Users, BookOpen } from "lucide-react";

// // export default function Dashboard() {
// //   const { userId } = useParams();
// //   const [user, setUser] = useState({});
// //   const [classes, setClasses] = useState([]);
// //   const [className, setClassName] = useState("");
// //   const [joinClassId, setJoinClassId] = useState("");

// //   useEffect(() => {
// //     API.get(`/users/${userId}`).then((res) => setUser(res.data));
// //     fetchClasses();
// //   }, []);

// //   const fetchClasses = () => {
// //     API.get(`/users/${userId}/classes`).then((res) => setClasses(res.data));
// //   };

// //   const createClass = async () => {
// //     if (!className.trim()) return;
// //     await API.post("/classes", {
// //       name: className,
// //       teacher_id: userId,
// //       students: [],
// //     });
// //     setClassName("");
// //     fetchClasses();
// //   };

// //   const joinClass = async () => {
// //     if (!joinClassId.trim()) return;
// //     await API.post(`/classes/${joinClassId}/join/${userId}`);
// //     setJoinClassId("");
// //     fetchClasses();
// //   };

// //   return (
// //     <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex flex-col items-center py-10 px-4">
// //       {/* Header */}
// //       <motion.div
// //         initial={{ opacity: 0, y: -20 }}
// //         animate={{ opacity: 1, y: 0 }}
// //         transition={{ duration: 0.5 }}
// //         className="w-full max-w-5xl flex justify-between items-center mb-10"
// //       >
// //         <h1 className="text-3xl font-bold text-white">
// //           👋 Welcome, <span className="text-yellow-300">{user.name}</span>
// //         </h1>
// //         <button className="bg-white/20 text-white px-4 py-2 rounded-xl hover:bg-white/30 transition flex items-center gap-2">
// //           <LogOut className="w-5 h-5" /> Logout
// //         </button>
// //       </motion.div>

// //       {/* Action Inputs */}
// //       <motion.div
// //         initial={{ opacity: 0, y: 10 }}
// //         animate={{ opacity: 1, y: 0 }}
// //         transition={{ delay: 0.2 }}
// //         className="bg-white/20 backdrop-blur-lg shadow-lg rounded-2xl p-6 w-full max-w-4xl mb-10"
// //       >
// //         {user.role === "teacher" && (
// //           <div className="flex flex-wrap gap-3 mb-4">
// //             <input
// //               type="text"
// //               placeholder="Enter new class name..."
// //               value={className}
// //               onChange={(e) => setClassName(e.target.value)}
// //               className="flex-1 p-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
// //             />
// //             <button
// //               onClick={createClass}
// //               className="bg-green-600 hover:bg-green-700 text-white px-5 py-3 rounded-xl flex items-center gap-2 font-medium transition-all"
// //             >
// //               <PlusCircle className="w-5 h-5" /> Create
// //             </button>
// //           </div>
// //         )}

// //         <div className="flex flex-wrap gap-3">
// //           <input
// //             type="text"
// //             placeholder="Enter class ID to join..."
// //             value={joinClassId}
// //             onChange={(e) => setJoinClassId(e.target.value)}
// //             className="flex-1 p-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none"
// //           />
// //           <button
// //             onClick={joinClass}
// //             className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl flex items-center gap-2 font-medium transition-all"
// //           >
// //             <Users className="w-5 h-5" /> Join
// //           </button>
// //         </div>
// //       </motion.div>

// //       {/* Classes Section */}
// //       <div className="w-full max-w-5xl">
// //         <h2 className="text-2xl font-semibold text-white mb-6">📚 Your Classes</h2>
// //         {classes.length === 0 ? (
// //           <p className="text-white/80 text-center italic">
// //             {user.role === "teacher"
// //               ? "You haven't created any classes yet."
// //               : "You haven't joined any classes yet."}
// //           </p>
// //         ) : (
// //           <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
// //             {classes.map((c, i) => (
// //               <motion.div
// //                 key={c.id}
// //                 initial={{ opacity: 0, y: 20 }}
// //                 animate={{ opacity: 1, y: 0 }}
// //                 transition={{ delay: i * 0.05 }}
// //                 className="bg-white/80 backdrop-blur-md rounded-2xl shadow-lg p-6 hover:shadow-2xl transition-all hover:-translate-y-1"
// //               >
// //                 <h3 className="text-xl font-bold text-gray-800 mb-2 flex items-center gap-2">
// //                   <BookOpen className="text-indigo-600" /> {c.name}
// //                 </h3>
// //                 <p className="text-gray-600 mb-4">Class ID: <span className="font-mono">{c.id}</span></p>
// //                 <Link
// //                   to={`/class/${c.id}/${userId}`}
// //                   className="inline-block text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl text-sm font-medium transition"
// //                 >
// //                   Open Class
// //                 </Link>
// //               </motion.div>
// //             ))}
// //           </div>
// //         )}
// //       </div>

// //       {/* Footer */}
// //       <p className="mt-12 text-white/70 text-sm">
// //         © 2025 Classroom Portal — Designed with ❤️ by <span className="font-semibold text-yellow-300">You</span>
// //       </p>
// //     </div>
// //   );
// // }


// import Navbar from "../components/Navbar";
// import { Link } from "react-router-dom";

// export default function Dashboard() {
//   return (
//     <>
//       <Navbar />
//       <div className="p-8 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
//         {[
//           { title: "Organizations", path: "/orgs" },
//           { title: "Departments", path: "/departments" },
//           { title: "Classes", path: "/classes" },
//           { title: "Assignments", path: "/assignments" },
//           { title: "Submissions", path: "/submissions" },
//           { title: "Notes", path: "/notes" },
//           { title: "Messages", path: "/messages" },
//           { title: "Grades", path: "/grades" },
//           { title: "Bulk Import", path: "/import" },
//         ].map((item) => (
//           <Link
//             key={item.title}
//             to={item.path}
//             className="bg-white shadow-md rounded-xl p-6 hover:shadow-lg border-t-4 border-indigo-600"
//           >
//             <h2 className="font-semibold text-indigo-600 text-lg">{item.title}</h2>
//           </Link>
//         ))}
//       </div>
//     </>
//   );
// }


import React from "react";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Welcome, {user.full_name || user.email}</h1>

      <div className="bg-white dark:bg-gray-800 shadow rounded-md p-4">
        <h2 className="text-lg font-medium mb-2">Your Details</h2>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Organization:</strong> {user.org_id || "N/A"}</p>
        <p><strong>Roles:</strong> {user.roles?.join(", ")}</p>
        <p><strong>Org Type:</strong> {user.org_type || "school"}</p>
      </div>
    </Layout>
  );
}
