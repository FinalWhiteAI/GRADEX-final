import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function HodDashboard() {
  const navigate=useNavigate()
  const [dept, setDept] = useState(null);
  const [teachers, setTeachers] = useState([]);
  const [classes, setClasses] = useState([]);
  const [section, setSection] = useState([]);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    section:""
  });

  const fetchDeptInfo = async () => {
  try {
    const me = await api.get("/api/users/me");

    const res = await api.get("/api/hod/department");

    const deptData = res.data;
    if (!deptData) {
      setDept(null);
      return;
    }

    setDept(deptData);

    const t = await api.get(`/api/departments/${deptData.id}/class-teachers`);
    setTeachers(t.data);

    const c = await api.get(`/api/departments/${deptData.id}/classes`);
    setClasses(c.data);
  } catch (err) {
    console.error("HOD dashboard err:", err);
  }
};


  const addTeacher = async () => {
  if (!form.email || !section) {
    alert("Enter details and section");
    return;
  }

  const fd = new FormData();
  fd.append("full_name", form.full_name);
  fd.append("email", form.email);
  fd.append("password", form.password);
  fd.append("section", section);

  try {
    await api.post(
      `/api/departments/${dept.id}/add-class-teacher`,
      fd,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    alert("Class Teacher added!");
    setForm({ full_name: "", email: "", password: "" });
    setSection("");
    fetchDeptInfo();
  } catch (err) {
    console.error(err);
    alert("Failed to add teacher");
  }
};



  useEffect(() => {
    fetchDeptInfo();
  }, []);

  if (!dept) return <Layout>Loading...</Layout>;
return (
  <Layout>
    <h1 className="text-3xl font-semibold mb-6 text-gray-900 dark:text-gray-100">
      HOD Dashboard
    </h1>

    {/* DEPARTMENT INFO */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mb-8 border dark:border-gray-700">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
        {dept.name}
      </h2>
      {/* <p className="text-gray-500 dark:text-gray-400 mt-1">
        Department ID: {dept.id}
      </p> */}
    </div>

    {/* ADD CLASS TEACHER */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mb-10 border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Add Class Teacher
      </h2>

      {/* Section */}
      <input
        type="text"
        placeholder="Section (Example: 5A)"
        value={section}
        onChange={(e) => setSection(e.target.value)}
        className="border dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 px-4 py-2 rounded-md w-full mb-3"
      />

      {/* Full Name */}
      <input
        className="border dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 px-4 py-2 rounded-md w-full mb-3"
        placeholder="Full Name"
        value={form.full_name}
        onChange={(e) => setForm({ ...form, full_name: e.target.value })}
      />

      {/* Email */}
      <input
        className="border dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 px-4 py-2 rounded-md w-full mb-3"
        placeholder="Email"
        type="email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />

      {/* Password */}
      <input
        className="border dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 px-4 py-2 rounded-md w-full mb-4"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />

      <button
        onClick={addTeacher}
        className="bg-green-600 hover:bg-green-700 transition text-white px-4 py-2 rounded-md shadow"
      >
        Add Teacher
      </button>
    </div>

    {/* TEACHER LIST */}
    <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
      Class Teachers
    </h2>

    <div className="grid md:grid-cols-2 gap-4 mb-10">
      {teachers.map((t) => (
        <div
          key={t.id}
          className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow border dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 transition"
        >
          <p className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
            {t.full_name}
          </p>
          <p className="text-gray-600 dark:text-gray-400 text-sm">{t.email}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Section: {t.section}
          </p>
        </div>
      ))}
    </div>

    {/* CLASS LIST */}
    <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
      Classes
    </h2>

    <div className="grid md:grid-cols-2 gap-4 mb-10">
      {classes.map((c) => (
        <div onClick={()=> navigate(`/class/${c.id}`)}
          key={c.id}
          className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow border dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 transition"
        >
          <p className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
            {c.title}
          </p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            {c.description}
          </p>
        </div>
      ))}
    </div>
  </Layout>
);

}

// import React, { useEffect, useState } from "react";
// import Layout from "../components/Layout";
// import api from "../api/axios";

// export default function HodDashboard() {
//   const [dept, setDept] = useState(null);
//   const [teachers, setTeachers] = useState([]);
//   const [classes, setClasses] = useState([]); // This is the "Class" (e.g., 10th Grade) list
  
//   // State for "Add Teacher" form
//   const [teacherFullName, setTeacherFullName] = useState("");
//   const [teacherEmail, setTeacherEmail] = useState("");
//   const [sectionName, setSectionName] = useState(""); // <-- FIX: Text input for section
  
//   const [loading, setLoading] = useState(true);
//   const [formLoading, setFormLoading] = useState(false);

//   const fetchDeptInfo = async () => {
//     try {
//       const deptRes = await api.get("/api/hod/department");
//       if (!deptRes.data || !deptRes.data.id) {
//         setDept(null);
//         setLoading(false);
//         return;
//       }
      
//       const deptData = deptRes.data;
//       setDept(deptData);
//       const dept_id = deptData.id;

//       const [teachersRes, classesRes] = await Promise.all([
//         api.get(`/api/departments/${dept_id}/class-teachers`),
//         api.get(`/api/departments/${dept_id}/classes`),
//       ]);

//       setTeachers(teachersRes.data || []);
//       setClasses(classesRes.data || []);
//     } catch (err) {
//       console.error("HOD dashboard err:", err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchDeptInfo();
//   }, []);


//   const handleAddTeacher = async (e) => {
//     e.preventDefault(); 
//     // FIX: Check sectionName from the text input
//     if (!teacherFullName || !teacherEmail || !sectionName) {
//       alert("Please fill in all fields and the section name (e.g., '5A').");
//       return;
//     }
//     setFormLoading(true);

//     // --- FIX: Use FormData to match your backend ---
//     const fd = new FormData();
//     fd.append("full_name", teacherFullName);
//     fd.append("email", teacherEmail);
//     fd.append("section", sectionName);

//     try {
//       await api.post(
//         `/api/departments/${dept.id}/add-class-teacher`,
//         fd, // Send FormData
//         { headers: { "Content-Type": "multipart/form-data" } } // Set header
//       );

//       alert("Class Teacher added!");
//       setTeacherFullName("");
//       setTeacherEmail("");
//       setSectionName(""); // Reset text input
//       fetchDeptInfo(); // Refresh list
//     } catch (err) {
//       console.error(err);
//       alert("Failed to add teacher. " + (err.response?.data?.detail || ""));
//     } finally {
//       setFormLoading(false);
//     }
//   };

//   // Helper styles
//   const inputClass =
//     "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white";
  
//   const buttonClass = (color = "green", isLoading = false) =>
//     `w-full justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-${color}-600 hover:bg-${color}-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${color}-500 disabled:opacity-50`;

//   if (loading) {
//     return <Layout><div className="p-6 text-center dark:text-white">Loading Dashboard...</div></Layout>;
//   }

//   if (!dept) {
//     return (
//       <Layout>
//         <div className="p-6 text-center">
//           <h1 className="text-xl font-semibold text-red-500">Error</h1>
//           <p className="dark:text-gray-300">Could not find department information for your account.</p>
//         </div>
//       </Layout>
//     );
//   }

//   return (
//     <Layout>
//       <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
//         HOD Dashboard
//       </h1>

//       {/* --- TOP ROW: Info & Form --- */}
//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        
//         {/* Card 1: Department Info */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg lg:col-span-1">
//           <h2 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
//             Your Department
//           </h2>
//           <div className="space-y-2">
//             <h3 className="text-3xl font-bold text-blue-600 dark:text-blue-400">{dept.name}</h3>
//             <p className="text-sm text-gray-500 dark:text-gray-400 font-mono">
//               ID: {dept.id}
//             </p>
//           </div>
//         </div>

//         {/* Card 2: Add Class Teacher */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg lg:col-span-2">
//           <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
//             Add New Class Teacher & Section
//           </h2>
//           <form onSubmit={handleAddTeacher} className="space-y-4">
//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               <div>
//                 <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
//                   Full Name
//                 </label>
//                 <input
//                   type="text"
//                   id="fullName"
//                   placeholder="e.g., 'John Doe'"
//                   className={inputClass}
//                   value={teacherFullName}
//                   onChange={(e) => setTeacherFullName(e.target.value)}
//                   required
//                 />
//               </div>
//               <div>
//                 <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
//                   Teacher Email
//                 </label>
//                 <input
//                   type="email"
//                   id="email"
//                   placeholder="teacher@example.com"
//                   className={inputClass}
//                   value={teacherEmail}
//                   onChange={(e) => setTeacherEmail(e.target.value)}
//                   required
//                 />
//               </div>
//             </div>

//             {/* --- FIX: Changed to text input for Section Name --- */}
//             <div>
//               <label htmlFor="sectionName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
//                 Assign New Section Name
//               </label>
//               <input
//                 type="text"
//                 id="sectionName"
//                 placeholder="e.g., '5A' or '10C'"
//                 className={inputClass}
//                 value={sectionName}
//                 onChange={(e) => setSectionName(e.target.value)}
//                 required
//               />
//             </div>

//             <button
//               type="submit"
//               disabled={formLoading}
//               className={buttonClass("green", formLoading)}
//             >
//               {formLoading ? "Adding..." : "Add Class Teacher"}
//             </button>
//           </form>
//         </div>
//       </div>

//       {/* --- BOTTOM ROW: Lists --- */}
//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
//         {/* List 1: Class Teachers */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//           <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
//             Class Teachers & Sections
//           </h2>
//           <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
//             {teachers.length > 0 ? (
//               teachers.map((t) => (
//                 <div key={t.id} className="border dark:border-gray-700 p-4 rounded-lg flex justify-between items-center">
//                   <div>
//                     <p className="font-medium text-gray-900 dark:text-white">{t.full_name}</p>
//                     <p className="text-sm text-gray-500 dark:text-gray-400">{t.email}</p>
//                   </div>
//                   <span className="text-sm font-semibold text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900 px-3 py-1 rounded-full">
//                     Section: {t.section}
//                   </span>
//                 </div>
//               ))
//             ) : (
//               <p className="text-gray-500 dark:text-gray-400 text-center py-4">
//                 No class teachers found.
//               </p>
//             )}
//           </div>
//         </div>

//         {/* List 2: Classes (e.g., 10th Grade, 11th Grade) */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//           <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
//             Classes
//           </h2>
//           <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
//             {classes.length > 0 ? (
//               classes.map((c) => (
//                 <div key={c.id} className="border dark:border-gray-700 p-4 rounded-lg">
//                   <p className="font-medium text-gray-900 dark:text-white">{c.title}</p>
//                   <p className="text-sm text-gray-500 dark:text-gray-400">{c.description}</p>
//                 </div>
//               ))
//             ) : (
//               <p className="text-gray-500 dark:text-gray-400 text-center py-4">
//                 No classes found for this department.
//               </p>
//             )}
//           </div>
//         </div>
//       </div>
//     </Layout>
//   );
// }
