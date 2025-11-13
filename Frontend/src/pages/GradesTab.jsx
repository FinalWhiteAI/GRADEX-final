// import React, { useEffect, useState } from "react";
// import api from "../api/axios";
// import { useAuth } from "../context/AuthContext";

// export default function GradesTab({ classId }) {
//   const { user } = useAuth();
//   const [grades, setGrades] = useState([]);
//   const [form, setForm] = useState({
//     student_id: "",
//     subject_name: "",
//     unit_name: "",
//     marks: "",
//   });

//   const fetchGrades = async () => {
//     const me = await api.get("/api/users/me");
//     const orgId = me.data.org_id;
//     const res = await api.get(`/api/orgs/${orgId}/grades`);
//     setGrades(res.data || []);
//   };

//   const uploadGrade = async () => {
//     try {
//       const me = await api.get("/api/users/me");
//       await api.post("/api/finalmarks", {
//         org_id: me.data.org_id,
//         class_id: classId,
//         ...form,
//       });
//       fetchGrades();
//       setForm({ student_id: "", subject_name: "", unit_name: "", marks: "" });
//     } catch {
//       alert("Only teachers can upload marks");
//     }
//   };

//   useEffect(() => {
//     fetchGrades();
//   }, []);

//   const canUpload = user?.roles?.includes("sub_teacher");

//   return (
//     <div>
//       {canUpload && (
//         <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
//           <h2 className="font-medium mb-2">Upload Final Mark</h2>
//           <div className="grid gap-2">
//             <input
//               placeholder="Student ID"
//               value={form.student_id}
//               onChange={(e) =>
//                 setForm({ ...form, student_id: e.target.value })
//               }
//               className="border px-3 py-1 rounded-md"
//             />
//             <input
//               placeholder="Subject"
//               value={form.subject_name}
//               onChange={(e) =>
//                 setForm({ ...form, subject_name: e.target.value })
//               }
//               className="border px-3 py-1 rounded-md"
//             />
//             <input
//               placeholder="Unit"
//               value={form.unit_name}
//               onChange={(e) => setForm({ ...form, unit_name: e.target.value })}
//               className="border px-3 py-1 rounded-md"
//             />
//             <input
//               placeholder="Marks"
//               type="number"
//               value={form.marks}
//               onChange={(e) => setForm({ ...form, marks: e.target.value })}
//               className="border px-3 py-1 rounded-md"
//             />
//             <button
//               onClick={uploadGrade}
//               className="bg-blue-600 text-white px-3 py-1 rounded-md"
//             >
//               Upload
//             </button>
//           </div>
//         </div>
//       )}

//       <h2 className="text-xl font-semibold mb-3">Final Marks</h2>
//       <ul className="space-y-2">
//         {grades.map((g) => (
//           <li key={g.id} className="bg-white dark:bg-gray-800 p-3 rounded-md shadow">
//             <p><strong>{g.subject_name}</strong> ({g.unit_name}) - {g.marks} marks</p>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }



import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function GradesTab({ classId }) {
  const { user } = useAuth();

  const [grades, setGrades] = useState([]);
  const [students, setStudents] = useState([]);

  const [form, setForm] = useState({
    student_id: "",
    subject_name: "",
    unit_name: "",
    marks: "",
  });

  // Fetch students for dropdown
  const fetchStudents = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}/students`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      // setStudents(res.data || []);
      const uniq = [];
const seen = new Set();

for (const s of res.data || []) {
  if (!seen.has(s.id)) {
    uniq.push(s);
    seen.add(s.id);
  }
}

setStudents(uniq);

    } catch (err) {
      console.error("Student fetch error", err);
    }
  };

  // Fetch class-only grades
  const fetchGrades = async () => {
    try {
      const res = await api.get(`/api/classes/${classId}/grades`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      setGrades(res.data || []);
    } catch (err) {
      console.error("Grades fetch error:", err);
    }
  };

  const uploadGrade = async () => {
    try {
      const me = await api.get("/api/users/me");

      await api.post("/api/finalmarks", {
        org_id: me.data.org_id,
        class_id: classId,
        ...form,
      });

      fetchGrades();
      setForm({ student_id: "", subject_name: "", unit_name: "", marks: "" });

    } catch (err) {
      alert("Only teachers can upload marks");
    }
  };

  useEffect(() => {
    fetchStudents();
    fetchGrades();
  }, []);

  const canUpload = user?.roles?.includes("sub_teacher");

  // Group subject wise
  const grouped = grades.reduce((acc, g) => {
    if (!acc[g.subject_name]) acc[g.subject_name] = [];
    acc[g.subject_name].push(g);
    return acc;
  }, {});

  return (
    <div>
      {canUpload && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-6">
          <h2 className="font-medium mb-2">Upload Final Mark</h2>

          {/* Student Dropdown */}
          <select
            value={form.student_id}
            onChange={(e) =>
              setForm({ ...form, student_id: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-2"
          >
            <option value="">Select Student</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.full_name} ({s.email})
              </option>
            ))}
          </select>

          <input
            placeholder="Subject"
            value={form.subject_name}
            onChange={(e) =>
              setForm({ ...form, subject_name: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-2"
          />

          <input
            placeholder="Unit"
            value={form.unit_name}
            onChange={(e) =>
              setForm({ ...form, unit_name: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-2"
          />

          <input
            placeholder="Marks"
            type="number"
            value={form.marks}
            onChange={(e) =>
              setForm({ ...form, marks: e.target.value })
            }
            className="border px-3 py-1 rounded-md mb-3"
          />

          <button
            onClick={uploadGrade}
            className="bg-blue-600 text-white px-3 py-1 rounded-md"
          >
            Upload
          </button>
        </div>
      )}

      <h2 className="text-xl font-semibold mb-3">Final Marks</h2>


{/* STUDENT VIEW → ONLY THEIR MARKS */}
{user.roles.includes("student") &&
  Object.keys(grouped).map((subject) => (
    <div
      key={subject}
      className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-4"
    >
      <h3 className="text-lg font-bold mb-2">{subject}</h3>

      {grouped[subject]
        .filter((g) => g.student_id === user.id)   // 👈 ONLY student's own marks
        .map((g) => (
          <p key={`${g.id}-${g.unit_name}`} className="text-gray-300">
            <strong>{g.unit_name}</strong>: {g.marks} marks
          </p>
        ))
      }
    </div>
  ))
}

{/* TEACHER VIEW → SEE ALL MARKS */}
{(user.roles.includes("sub_teacher") ||
  user.roles.includes("class_teacher") ||
  user.roles.includes("admin")) &&
  Object.keys(grouped).map((subject) => (
    <div
      key={subject}
      className="bg-white dark:bg-gray-800 p-4 rounded-md shadow mb-4"
    >
      <h3 className="text-lg font-bold mb-2">{subject}</h3>

      {grouped[subject].map((g) => (
        <p key={`${g.id}-${g.unit_name}-${g.student_id}`} className="text-gray-300">
          <strong>{g.unit_name}</strong>: {g.marks} marks (Student: {g.student_id})
        </p>
      ))}
    </div>
  ))
}

{grades.length === 0 && <p>No grades yet.</p>}
    </div>
  );
}
