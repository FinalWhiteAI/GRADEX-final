// import React, { useEffect, useState } from "react";
// import Layout from "../components/Layout";
// import api from "../api/axios";
// import { useNavigate } from "react-router-dom";

// export default function TeacherDashboard() {
//   const [classes, setClasses] = useState([]);
//     const navigate=useNavigate()

//   const [newSubTeacher, setNewSubTeacher] = useState({
//     email: "",
//     full_name: "",
//     password:""
//   });

//   const fetchClasses = async () => {
//     const res = await api.get("/api/classes");
//     setClasses(res.data || []);
//   };

//   const addSubTeacher = async () => {
//     if (!newSubTeacher.email) return alert("Enter sub-teacher email");
//     try {
//       await api.post("/api/teachers/add-sub", newSubTeacher);
//       alert("Sub teacher added");
//       setNewSubTeacher({ email: "", full_name: "",password:"" });
//     } catch {
//       alert("Failed to add sub-teacher");
//     }
//   };

//   useEffect(() => {
//     fetchClasses();
//   }, []);

//   return (
//     <Layout>
//       <h1 className="text-2xl font-semibold mb-4">Class Teacher Dashboard</h1>
//      <div className="grid md:grid-cols-2 gap-4">
//         {classes.length === 0 && <p>No classes yet.</p>}
//         {classes.map((cls) => (
//           <div
//             key={cls.id}
//             className="bg-white dark:bg-gray-800 p-4 rounded-md shadow flex flex-col justify-between"
//           >
//             <div>
//               <h2 className="text-lg font-semibold">{cls.title}</h2>
//               <p className="text-gray-500">{cls.description}</p>
//               <p className="text-sm mt-1 text-gray-400">Code: {cls.class_code}</p>
//             </div>

//             <div className="mt-3 flex justify-end">
//               <button
//                 onClick={() => navigate(`/class/${cls.id}`)}
//                 className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md"
//               >
//                 View Class
//               </button>
//             </div>
//           </div>
//         ))}
//       </div>


//       <div className="bg-white dark:bg-gray-800 p-4 rounded-md mt-6 shadow">
//         <h2 className="font-medium mb-2">Add Subject Teacher</h2>
//         <div className="flex flex-col gap-2">
//           <input
//             type="text"
//             placeholder="Full Name"
//             className="border px-3 py-1 rounded-md"
//             value={newSubTeacher.full_name}
//             onChange={(e) =>
//               setNewSubTeacher({ ...newSubTeacher, full_name: e.target.value })
//             }
//           />
//           <input
//             type="email"
//             placeholder="Email"
//             className="border px-3 py-1 rounded-md"
//             value={newSubTeacher.email}
//             onChange={(e) =>
//               setNewSubTeacher({ ...newSubTeacher, email: e.target.value })
//             }
//           /><input
//             type="text"
//             placeholder="Password"
//             className="border px-3 py-1 rounded-md"
//             value={newSubTeacher.password}
//             onChange={(e) =>
//               setNewSubTeacher({ ...newSubTeacher, password: e.target.value })
//             }
//           />
//           <button
//             onClick={addSubTeacher}
//             className="bg-green-600 text-white px-3 py-1 rounded-md"
//           >
//             Add Sub Teacher
//           </button>
//         </div>
//       </div>
//     </Layout>
//   );
// }


import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function TeacherDashboard() {
  const [classes, setClasses] = useState([]);
  const [newSubTeacher, setNewSubTeacher] = useState({
    email: "",
    full_name: "",
    password: ""
  });
  const [newStudent, setNewStudent] = useState({
    class_id: "",
    full_name: "",
    email: "",
    password: ""
  });
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const fetchClasses = async () => {
    const res = await api.get("/api/classes", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    setClasses(res.data || []);
  };

  const addSubTeacher = async () => {
    if (!newSubTeacher.email) return alert("Enter sub-teacher email");
    try {
      await api.post("/api/teachers/add-sub", newSubTeacher, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      alert("Sub-teacher added");
      setNewSubTeacher({ email: "", full_name: "", password: "" });
    } catch {
      alert("Failed to add sub-teacher");
    }
  };

  const addStudent = async () => {
    if (!newStudent.class_id || !newStudent.email) {
      return alert("Enter all student details");
    }
    try {
      await api.post(
        "/api/teachers/add-student",
        newStudent,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }
      );
      alert("Student added successfully!");
      setNewStudent({ class_id: "", full_name: "", email: "", password: "" });
    } catch (err) {
      console.error("Add student error:", err);
      alert("Failed to add student");
    }
  };

  const importStudents = async () => {
    if (!file) return alert("Upload an Excel or CSV file");
    const formData = new FormData();
    formData.append("file", file);
    try {
    await api.post(`/api/teachers/import-students?class_id=${encodeURIComponent(newStudent.class_id)}`, formData, {

        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "multipart/form-data",
        },
      });
      alert("Students imported successfully!");
      setFile(null);
    } catch (err) {
      console.error("Import error:", err);
      alert("Import failed");
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Class Teacher Dashboard</h1>

      {/* CLASS LIST */}
      <div className="grid md:grid-cols-2 gap-4">
        {classes.map((cls) => (
          <div
            key={cls.id}
            className="bg-white dark:bg-gray-800 p-4 rounded-md shadow"
          >
            <h2 className="text-lg font-semibold">{cls.title}</h2>
            <p className="text-gray-500">{cls.description}</p>
            <p className="text-sm text-gray-400 mt-1">
              Code: {cls.class_code}
            </p>
            <button
              className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md"
              onClick={() => navigate(`/class/${cls.id}`)}
            >
              View Class
            </button>
          </div>
        ))}
      </div>

      {/* ADD SUB-TEACHER */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mt-6 shadow">
        <h2 className="font-medium mb-2">Add Subject Teacher</h2>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name"
            className="border px-3 py-1 rounded-md"
            value={newSubTeacher.full_name}
            onChange={(e) =>
              setNewSubTeacher({ ...newSubTeacher, full_name: e.target.value })
            }
          />
          <input
            type="email"
            placeholder="Email"
            className="border px-3 py-1 rounded-md"
            value={newSubTeacher.email}
            onChange={(e) =>
              setNewSubTeacher({ ...newSubTeacher, email: e.target.value })
            }
          />
          <input
            type="text"
            placeholder="Password"
            className="border px-3 py-1 rounded-md"
            value={newSubTeacher.password}
            onChange={(e) =>
              setNewSubTeacher({ ...newSubTeacher, password: e.target.value })
            }
          />
          <button
            onClick={addSubTeacher}
            className="bg-green-600 text-white px-3 py-1 rounded-md"
          >
            Add Sub-Teacher
          </button>
        </div>
      </div>

      {/* ADD STUDENT SECTION */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-md mt-6 shadow">
        <h2 className="font-medium mb-2">Add Student</h2>

        <select
          className="border px-3 py-1 rounded-md mb-2"
          value={newStudent.class_id}
          onChange={(e) =>
            setNewStudent({ ...newStudent, class_id: e.target.value })
          }
        >
          <option value="">Select Class</option>
          {classes.map((cls) => (
            <option key={cls.id} value={cls.id}>
              {cls.title}
            </option>
          ))}
        </select>

        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name"
            className="border px-3 py-1 rounded-md"
            value={newStudent.full_name}
            onChange={(e) =>
              setNewStudent({ ...newStudent, full_name: e.target.value })
            }
          />
          <input
            type="email"
            placeholder="Email"
            className="border px-3 py-1 rounded-md"
            value={newStudent.email}
            onChange={(e) =>
              setNewStudent({ ...newStudent, email: e.target.value })
            }
          />
          <input
            type="text"
            placeholder="Password"
            className="border px-3 py-1 rounded-md"
            value={newStudent.password}
            onChange={(e) =>
              setNewStudent({ ...newStudent, password: e.target.value })
            }
          />
          <button
            onClick={addStudent}
            className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md"
          >
            Add Student Manually
          </button>
        </div>

        <hr className="my-4 border-gray-500" />

        <h2 className="font-medium mb-2">Import Students via Excel</h2>
        <select
  className="border px-3 py-1 rounded-md mb-2"
  value={newStudent.class_id}
  onChange={(e) => setNewStudent({ ...newStudent, class_id: e.target.value })}
>
  <option value="">Select Class</option>
  {classes.map((cls) => (
    <option key={cls.id} value={cls.id}>
      {cls.title}
    </option>
  ))}
</select>

        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={(e) => setFile(e.target.files[0])}
          className="border px-3 py-1 rounded-md"
        />
        <button
          onClick={importStudents}
          className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md"
        >
          Upload File
        </button>
      </div>
    </Layout>
  );
}
