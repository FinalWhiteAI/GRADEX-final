
import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function AdminDashboard() {
  const [departments, setDepartments] = useState([]);
  const [newDept, setNewDept] = useState("");
  const [hodForm, setHodForm] = useState({
    dept_id: "",
    full_name: "",
    email: "",
    password: "",
  });

  const fetchDepartments = async () => {
    try {
      const me = await api.get("/api/users/me");
      const orgId = me.data.org_id;

      const res = await api.get(`/api/orgs/${orgId}/departments`);
      setDepartments(res.data || []);
    } catch (err) {
      console.error("Dept fetch error:", err);
    }
  };

  const addDepartment = async () => {
    if (!newDept) return alert("Enter department name");

    try {
      const me = await api.get("/api/users/me");

      await api.post("/api/departments/create", {
        org_id: me.data.org_id,
        name: newDept,
      });

      setNewDept("");
      fetchDepartments();
    } catch (err) {
      console.error(err);
      alert("Failed to create department");
    }
  };

  const assignHod = async () => {
    if (!hodForm.dept_id) return alert("Select department");

    try {
      const me = await api.get("/api/users/me");

      await api.post(
        `/api/orgs/${me.data.org_id}/departments/${hodForm.dept_id}/assign-hod`,
        hodForm
      );

      alert("HOD Assigned");
      setHodForm({
        dept_id: "",
        full_name: "",
        email: "",
        password: "",
      });
    } catch (err) {
      console.error("Assign HOD error:", err);
      alert("Failed to assign HOD");
    }
  };

  useEffect(() => {
    fetchDepartments();
  }, []);
return (
  <Layout>
    <h1 className="text-3xl font-semibold mb-6 text-gray-900 dark:text-gray-100">
      Admin Dashboard
    </h1>

    {/* ADD DEPARTMENT */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mb-8 border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Add Department
      </h2>

      <div className="flex gap-3">
        <input
          className="border px-4 py-2 rounded-md w-full dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          placeholder="Department Name"
          value={newDept}
          onChange={(e) => setNewDept(e.target.value)}
        />
        <button
          onClick={addDepartment}
          className="bg-blue-600 hover:bg-blue-700 transition text-white px-4 py-2 rounded-md shadow"
        >
          Add
        </button>
      </div>
    </div>

    {/* ASSIGN HOD */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mb-8 border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Assign HOD
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Department Selector */}
        <select
          className="border px-4 py-2 rounded-md w-full dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          value={hodForm.dept_id}
          onChange={(e) => setHodForm({ ...hodForm, dept_id: e.target.value })}
        >
          <option value="">Select Department</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>

        {/* Full Name */}
        <input
          className="border px-4 py-2 rounded-md w-full dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          placeholder="Full Name"
          value={hodForm.full_name}
          onChange={(e) =>
            setHodForm({ ...hodForm, full_name: e.target.value })
          }
        />

        {/* Email */}
        <input
          className="border px-4 py-2 rounded-md w-full dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          placeholder="Email"
          type="email"
          value={hodForm.email}
          onChange={(e) =>
            setHodForm({ ...hodForm, email: e.target.value })
          }
        />

        {/* Password */}
        <input
          className="border px-4 py-2 rounded-md w-full dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          placeholder="Password"
          value={hodForm.password}
          onChange={(e) =>
            setHodForm({ ...hodForm, password: e.target.value })
          }
        />
      </div>

      <button
        onClick={assignHod}
        className="mt-4 bg-green-600 hover:bg-green-700 transition text-white px-4 py-2 rounded-md shadow"
      >
        Assign HOD
      </button>
    </div>

    {/* LIST DEPARTMENTS */}
    <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
      Departments
    </h2>

    <div className="grid md:grid-cols-2 gap-4">
      {departments.map((d) => (
        <div
          key={d.id}
          className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow border dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 transition"
        >
          <p className="font-medium text-gray-900 dark:text-gray-100 text-lg">
            {d.name}
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

// export default function AdminDashboard() {
//   const [departments, setDepartments] = useState([]);
//   const [newDept, setNewDept] = useState("");
  
//   // CHANGED: Removed 'password' from the initial state
//   const [hodForm, setHodForm] = useState({
//     dept_id: "",
//     full_name: "",
//     email: "",
//   });

//   const fetchDepartments = async () => {
//     try {
//       const me = await api.get("/api/users/me");
//       const orgId = me.data.org_id;

//       const res = await api.get(`/api/orgs/${orgId}/departments`);
//       setDepartments(res.data || []);
//     } catch (err) {
//       console.error("Dept fetch error:", err);
//     }
//   };

//   const addDepartment = async () => {
//     if (!newDept) return alert("Enter department name");

//     try {
//       const me = await api.get("/api/users/me");

//       await api.post("/api/departments/create", {
//         org_id: me.data.org_id,
//         name: newDept,
//       });

//       setNewDept("");
//       fetchDepartments();
//     } catch (err) {
//       console.error(err);
//       alert("Failed to create department");
//     }
//   };

//   const assignHod = async () => {
//     if (!hodForm.dept_id) return alert("Select department");

//     try {
//       const me = await api.get("/api/users/me");

//       // CHANGED: Create a payload with only what the AddUserReq model needs
//       const payload = {
//         full_name: hodForm.full_name,
//         email: hodForm.email,
//         roles: ["hod"], // Backend will handle this, but it's good to be explicit
//       };

//       await api.post(
//         `/api/orgs/${me.data.org_id}/departments/${hodForm.dept_id}/assign-hod`,
//         payload // Send the new payload, not the whole form state
//       );

//       alert("HOD Assigned");
      
//       // CHANGED: Removed 'password' from the reset
//       setHodForm({
//         dept_id: "",
//         full_name: "",
//         email: "",
//       });
//     } catch (err) {
//       console.error("Assign HOD error:", err);
//       alert("Failed to assign HOD");
//     }
//   };

//   useEffect(() => {
//     fetchDepartments();
//   }, []);

//   return (
//     <Layout>
//       <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

//       {/* ADD DEPARTMENT (No changes needed) */}
//       <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
//         <h2 className="text-lg font-semibold mb-2">Add Department</h2>
//         <div className="flex gap-2">
//           <input
//             className="border px-3 py-1 rounded-md w-full"
//             placeholder="Department Name"
//             value={newDept}
//             onChange={(e) => setNewDept(e.target.value)}
//           />
//           <button
//             onClick={addDepartment}
//             className="bg-blue-600 text-white px-3 py-1 rounded-md"
//           >
//             Add
//           </button>
//         </div>
//       </div>

//       {/* ASSIGN HOD (Password field removed) */}
//       <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
//         <h2 className="text-lg font-semibold mb-2">Assign HOD</h2>

//         <select
//           className="border px-3 py-1 rounded-md w-full mb-2"
//           value={hodForm.dept_id}
//           onChange={(e) =>
//             setHodForm({ ...hodForm, dept_id: e.target.value })
//           }
//         >
//           <option value="">Select Department</option>
//           {departments.map((d) => (
//             <option key={d.id} value={d.id}>
//               {d.name}
//             </option>
//           ))}
//         </select>

//         <input
//           className="border px-3 py-1 rounded-md w-full mb-2"
//           placeholder="Full Name"
//           value={hodForm.full_name}
//           onChange={(e) =>
//             setHodForm({ ...hodForm, full_name: e.target.value })
//           }
//         />
//         <input
//           className="border px-3 py-1 rounded-md w-full mb-2"
//           placeholder="Email"
//           type="email"
//           value={hodForm.email}
//           onChange={(e) =>
//             setHodForm({ ...hodForm, email: e.target.value })
//           }
//         />
        
//         {/* REMOVED: Password input field */}
//         {/*
//         <input
//           className="border px-3 py-1 rounded-md w-full mb-2"
//           placeholder="Password"
//           value={hodForm.password}
//           onChange={(e) =>
//             setHodForm({ ...hodForm, password: e.target.value })
//           }
//         />
//         */}

//         <button
//           onClick={assignHod}
//           className="bg-green-600 text-white px-3 py-1 rounded-md"
//         >
//           Assign HOD
//         </button>
//       </div>

//       {/* LIST DEPARTMENTS (No changes needed) */}
//       <h2 className="text-xl font-bold mb-3">Departments</h2>
//       <div className="grid md:grid-cols-2 gap-4">
//         {departments.map((d) => (
//           <div
//             key={d.id}
//             className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
//           >
//             <p className="font-medium">{d.name}</p>
//           </div>
//         ))}
//       </div>
//     </Layout>
//   );
// }