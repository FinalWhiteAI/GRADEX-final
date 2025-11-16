

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

      
      <div className="bg-white  dark:bg-gray-800 p-4 rounded-md mt-6 shadow ">
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
          className="border px-3 py-1 rounded-md text-blue-500 mb-2"
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
  className="border px-3 py-1 text-blue-500 rounded-md mb-2 "
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


// import React, { useEffect, useState } from "react";
// import Layout from "../components/Layout";
// import api from "../api/axios";
// import { useAuth } from "../context/AuthContext";

// export default function TeacherDashboard() {
//   const { currentUser } = useAuth();
  
//   // Role checks
//   const roles = currentUser?.roles || [];
//   const isClassTeacher = roles.includes("class_teacher");
//   const isSubjectTeacher = roles.includes("teacher");

//   // Data states
//   const [mySection, setMySection] = useState(null);
//   const [students, setStudents] = useState([]);
//   const [mySubjects, setMySubjects] = useState([]);
//   const [loading, setLoading] = useState(true);

//   // Form states
//   const [studentName, setStudentName] = useState("");
//   const [studentEmail, setStudentEmail] = useState("");
//   const [subjectName, setSubjectName] = useState("");
//   const [teacherEmail, setTeacherEmail] = useState("");
  
//   const [studentFormLoading, setStudentFormLoading] = useState(false);
//   const [subjectFormLoading, setSubjectFormLoading] = useState(false);

//   // Fetch all data based on user's roles
//   const fetchData = async () => {
//     try {
//       const promises = [];
      
//       if (isClassTeacher) {
//         promises.push(api.get("/api/class-teacher/my-section")); // Get "5A"
//         promises.push(api.get("/api/class-teacher/students")); // Get students in "5A"
//       }
//       if (isSubjectTeacher) {
//         promises.push(api.get("/api/teacher/my-subjects")); // Get subjects
//       }

//       const results = await Promise.all(promises);
      
//       let promiseIndex = 0;
//       if (isClassTeacher) {
//         setMySection(results[promiseIndex].data);
//         promiseIndex++;
//         setStudents(results[promiseIndex].data);
//         promiseIndex++;
//       }
//       if (isSubjectTeacher) {
//         setMySubjects(results[promiseIndex].data);
//       }

//     } catch (err) {
//       console.error("Failed to fetch dashboard data:", err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchData();
//   }, [currentUser]); // Re-fetch if user changes

//   // --- NEW: Add Student Function ---
//   const handleAddStudent = async (e) => {
//     e.preventDefault();
//     setStudentFormLoading(true);
//     try {
//       await api.post("/api/class-teacher/add-student", {
//         full_name: studentName,
//         email: studentEmail,
//       });
//       alert("Student added successfully!");
//       setStudentName("");
//       setStudentEmail("");
//       fetchData(); // Refresh lists
//     } catch (err) {
//       console.error(err);
//       alert("Failed to add student: " + (err.response?.data?.detail || "Error"));
//     } finally {
//       setStudentFormLoading(false);
//     }
//   };

//   // --- Assign Subject Teacher Function (from last time) ---
//   const handleAssignSubject = async (e) => {
//     e.preventDefault();
//     setSubjectFormLoading(true);
//     try {
//       await api.post("/api/class-teacher/assign-subject-teacher", {
//         subject_name: subjectName,
//         teacher_email: teacherEmail,
//       });
//       alert("Subject teacher assigned!");
//       setSubjectName("");
//       setTeacherEmail("");
//       fetchData(); // Refresh lists
//     } catch (err) {
//       console.error(err);
//       alert("Failed to assign teacher: " + (err.response?.data?.detail || "Error"));
//     } finally {
//       setSubjectFormLoading(false);
//     }
//   };
  
//   // Helper styles
//   const inputClass =
//     "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white";
//   const buttonClass = (color, isLoading) =>
//     `w-full justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-${color}-600 hover:bg-${color}-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${color}-500 disabled:opacity-50`;

//   if (loading) {
//     return <Layout><div className="p-6 text-center dark:text-white">Loading...</div></Layout>;
//   }

//   return (
//     <Layout>
//       <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
//         Teacher Dashboard
//       </h1>

//       {/* --- Main Grid --- */}
//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

//         {/* === COLUMN 1: FORMS === */}
//         <div className="space-y-6">
          
//           {/* --- Show this card if user is a CLASS TEACHER --- */}
//           {isClassTeacher && (
//             <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//               <h2 className="text-xl font-semibold mb-1 text-gray-900 dark:text-white">Add Student to Your Section</h2>
//               {mySection && <p className="text-blue-600 dark:text-blue-400 font-medium mb-4">Section: {mySection.section}</p>}
              
//               <form onSubmit={handleAddStudent} className="space-y-4">
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Student Full Name</label>
//                   <input
//                     type="text" placeholder="e.g., 'Sam Smith'" className={inputClass}
//                     value={studentName} onChange={(e) => setStudentName(e.target.value)} required
//                   />
//                 </div>
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Student Email</label>
//                   <input
//                     type="email" placeholder="student@example.com" className={inputClass}
//                     value={studentEmail} onChange={(e) => setStudentEmail(e.target.value)} required
//                   />
//                 </div>
//                 <button type="submit" disabled={studentFormLoading} className={buttonClass("blue", studentFormLoading)}>
//                   {studentFormLoading ? "Adding..." : "Add Student"}
//                 </button>
//               </form>
//             </div>
//           )}
          
//           {/* --- Show this card if user is a SUBJECT TEACHER --- */}
//           {/* (Or if they are a class teacher who can assign other teachers) */}
//           {isClassTeacher && (
//             <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//               <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Assign Subject Teacher</h2>
              
//               <button onClick={() => setTeacherEmail(currentUser.email)}
//                 className="mb-4 text-sm text-blue-600 hover:underline">
//                 Click here to assign yourself
//               </button>
              
//               <form onSubmit={handleAssignSubject} className="space-y-4">
//                  <div>
//                   <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Subject Name</label>
//                   <input
//                     type="text" placeholder="e.g., Mathematics" className={inputClass}
//                     value={subjectName} onChange={(e) => setSubjectName(e.target.value)} required
//                   />
//                 </div>
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Teacher's Email</label>
//                   <input
//                     type="email" placeholder="teacher@example.com" className={inputClass}
//                     value={teacherEmail} onChange={(e) => setTeacherEmail(e.target.value)} required
//                   />
//                 </div>
//                 <button type="submit" disabled={subjectFormLoading} className={buttonClass("green", subjectFormLoading)}>
//                   {subjectFormLoading ? "Assigning..." : "Assign Teacher"}
//                 </button>
//               </form>
//             </div>
//           )}
//         </div>
        
//         {/* === COLUMN 2: DATA LISTS === */}
//         <div className="space-y-6">
          
//           {/* --- Show this card if user is a CLASS TEACHER --- */}
//           {isClassTeacher && (
//             <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//               <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Students in Your Section</h2>
//               <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
//                 {students.length > 0 ? (
//                   students.map((student) => (
//                     <div key={student.id} className="border dark:border-gray-700 p-3 rounded-lg">
//                       <p className="font-medium text-gray-900 dark:text-white">{student.full_name}</p>
//                       <p className="text-sm text-gray-500 dark:text-gray-400">{student.email}</p>
//                     </div>
//                   ))
//                 ) : (
//                   <p className="text-gray-500 dark:text-gray-400 text-center py-4">No students found.</p>
//                 )}
//               </div>
//             </div>
//           )}

//           {/* --- Show this card if user is a SUBJECT TEACHER --- */}
//           {isSubjectTeacher && (
//             <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//               <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Your Assigned Subjects</h2>
//               <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
//                 {mySubjects.length > 0 ? (
//                   mySubjects.map((sub) => (
//                     <div key={sub.id} className="border dark:border-gray-700 p-3 rounded-lg">
//                       <p className="font-medium text-gray-900 dark:text-white">{sub.subject_name}</p>
//                       <p className="text-sm text-gray-500 dark:text-gray-400">Section: {sub.section}</p>
//                     </div>
//                   ))
//                 ) : (
//                   <p className="text-gray-500 dark:text-gray-400 text-center py-4">You are not assigned to any subjects.</p>
//                 )}
//               </div>
//             </div>
//           )}
//         </div>
//       </div>
//     </Layout>
//   );
// }