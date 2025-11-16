import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/axios";

export default function OwnerDashboard() {
  const [orgs, setOrgs] = useState([]);
  const [newOrg, setNewOrg] = useState({ name: "", org_type: "school" });
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [orgId, setOrgId] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");

  const fetchOrgs = async () => {
    const res = await api.get("/api/orgs");
    setOrgs(res.data);
  };

  const createOrg = async () => {
    if (!newOrg.name) return alert("Enter org name");
    setLoading(true);
    try {
      await api.post("/api/orgs", newOrg);
      fetchOrgs();
      setNewOrg({ name: "", org_type: "school" });
    } finally {
      setLoading(false);
    }
  };

  const createAdmin = async () => {
    if (!orgId || !email) return alert("Enter all fields");
    setLoading(true);
    try {
      await api.post(`/api/orgs/${orgId}/admin/create`, {
        email,
        full_name: fullName,
        password

      });
      alert("Admin created");
      setEmail("");
      setFullName("");
      setOrgId("");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrgs();
  }, []);
return (
  <Layout>
    <h1 className="text-3xl font-semibold mb-6 text-gray-900 dark:text-gray-100">
      Owner Dashboard
    </h1>

    {/* Org creation */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mb-8 border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Create Organization
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Name */}
        <input
          type="text"
          placeholder="Organization Name"
          value={newOrg.name}
          onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
        />

        {/* City (Display only) */}
        <input
          type="text"
          placeholder="City"
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
        />

        {/* State (Display only) */}
        <input
          type="text"
          placeholder="State"
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
        />

        {/* Type */}
        <select
          value={newOrg.org_type}
          onChange={(e) => setNewOrg({ ...newOrg, org_type: e.target.value })}
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
        >
          <option value="school">School</option>
          <option value="college">College</option>
          <option value="university">University</option>
        </select>
      </div>

      <button
        onClick={createOrg}
        disabled={loading}
        className="mt-4 bg-blue-600 hover:bg-blue-700 transition text-white px-4 py-2 rounded-md shadow"
      >
        {loading ? "Creating..." : "Create Organization"}
      </button>
    </div>

    {/* Org list */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Organizations
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b dark:border-gray-700 bg-gray-100 dark:bg-gray-900">
              <th className="py-3 px-2">Name</th>
              <th className="px-2">Type</th>
              <th className="px-2">ID</th>
            </tr>
          </thead>
          <tbody>
            {orgs.map((o) => (
              <tr
                key={o.id}
                className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 transition"
              >
                <td className="py-3 px-2">{o.name}</td>
                <td className="px-2">{o.org_type}</td>
                <td className="px-2 font-mono text-xs">{o.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>

    {/* Create admin */}
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg mt-8 border dark:border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Create Admin
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Full Name"
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />

        <input
          type="email"
          placeholder="Admin Email"
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password (optional)"
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <select
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
          className="border px-3 py-2 rounded-md dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
        >
          <option value="">Select Organization</option>
          {orgs.map((o) => (
            <option key={o.id} value={o.id}>
              {o.name}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={createAdmin}
        className="mt-4 bg-green-600 hover:bg-green-700 transition text-white px-4 py-2 rounded-md shadow"
      >
        Create Admin
      </button>
    </div>
  </Layout>
);

}

// import React, { useEffect, useState } from "react";
// import Layout from "../components/Layout";
// import api from "../api/axios";

// export default function OwnerDashboard() {
//   const [orgs, setOrgs] = useState([]);
  
//   // Updated state for new org fields
//   const [newOrg, setNewOrg] = useState({
//     name: "",
//     org_type: "school",
//     city: "",
//     state: "",
//   });
  
//   const [loading, setLoading] = useState(false);
//   const [adminLoading, setAdminLoading] = useState(false);

//   // Admin form state (Password REMOVED)
//   const [email, setEmail] = useState("");
//   const [orgId, setOrgId] = useState("");
//   const [fullName, setFullName] = useState("");

//   const fetchOrgs = async () => {
//     try {
//       const res = await api.get("/api/orgs");
//       setOrgs(res.data);
//     } catch (error) {
//       console.error("Failed to fetch organizations:", error);
//       alert("Failed to load organizations.");
//     }
//   };

//   const handleCreateOrg = async (e) => {
//     e.preventDefault();
//     // Updated validation
//     if (!newOrg.name || !newOrg.city || !newOrg.state) {
//        return alert("Please fill in org name, city, and state.");
//     }
    
//     setLoading(true);
//     try {
//       // API call now sends all fields
//       await api.post("/api/orgs", newOrg); 
//       fetchOrgs();
      
//       // Reset form (including new fields)
//       setNewOrg({ name: "", org_type: "school", city: "", state: "" }); 
//       alert("Organization created successfully!");
//     } catch (error) {
//       console.error("Failed to create org:", error);
//       alert("Failed to create organization.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleCreateAdmin = async (e) => {
//     e.preventDefault();
//     // Updated validation (Password REMOVED)
//     if (!orgId || !email || !fullName) {
//       return alert("Please fill in all admin fields.");
//     }
//     setAdminLoading(true);
//     try {
//       // API call now only sends email and name
//       await api.post(`/api/orgs/${orgId}/admin/create`, {
//         email,
//         full_name: fullName,
//       });
//       alert("Admin created");
//       setEmail("");
//       setFullName("");
//       setOrgId("");
//     } catch (error) {
//       console.error("Failed to create admin:", error);
//       alert("Failed to create admin. Check console for details.");
//     } finally {
//       setAdminLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchOrgs();
//   }, []);

//   const inputClass =
//     "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white";

//   const buttonClass = (color = "blue", isLoading = false) =>
//     `w-full justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-${color}-600 hover:bg-${color}-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${color}-500 disabled:opacity-50`;

//   return (
//     <Layout>
//       <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
//         Owner Dashboard
//       </h1>

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
//         {/* --- Card 1: Create Organization --- */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//           <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
//             Create New Organization
//           </h2>
//           <form onSubmit={handleCreateOrg} className="space-y-4">
//             {/* Org Name */}
//             <div>
//               <label
//                 htmlFor="orgName"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 Organization Name
//               </label>
//               <input
//                 type="text"
//                 id="orgName"
//                 placeholder="e.g., 'Greenwood High'"
//                 value={newOrg.name}
//                 onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
//                 className={inputClass}
//                 required
//               />
//             </div>
            
//             {/* Org Type */}
//             <div>
//               <label
//                 htmlFor="orgType"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 Organization Type
//               </label>
//               <select
//                 id="orgType"
//                 value={newOrg.org_type}
//                 onChange={(e) =>
//                   setNewOrg({ ...newOrg, org_type: e.target.value })
//                 }
//                 className={inputClass}
//               >
//                 <option value="school">School</option>
//                 <option value="college">College</option>
//                 <option value="university">University</option>
//               </select>
//             </div>
            
//             {/* --- NEW: City --- */}
//              <div>
//               <label
//                 htmlFor="orgCity"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 City
//               </label>
//               <input
//                 type="text"
//                 id="orgCity"
//                 placeholder="e.g., 'Springfield'"
//                 value={newOrg.city}
//                 onChange={(e) => setNewOrg({ ...newOrg, city: e.target.value })}
//                 className={inputClass}
//                 required
//               />
//             </div>
            
//             {/* --- NEW: State --- */}
//             <div>
//               <label
//                 htmlFor="orgState"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 State
//               </label>
//               <input
//                 type="text"
//                 id="orgState"
//                 placeholder="e.g., 'Illinois'"
//                 value={newOrg.state}
//                 onChange={(e) => setNewOrg({ ...newOrg, state: e.target.value })}
//                 className={inputClass}
//                 required
//               />
//             </div>

//             <button
//               type="submit"
//               disabled={loading}
//               className={buttonClass("blue", loading)}
//             >
//               {loading ? "Creating..." : "Create Organization"}
//             </button>
//           </form>
//         </div>

//         {/* --- Card 2: Create Admin --- */}
//         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
//           <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
//             Create New Admin
//           </h2>
//           <form onSubmit={handleCreateAdmin} className="space-y-4">
//             {/* Full Name */}
//             <div>
//               <label
//                 htmlFor="fullName"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 Full Name
//               </label>
//               <input
//                 type="text"
//                 id="fullName"
//                 placeholder="e.g., 'Jane Doe'"
//                 className={inputClass}
//                 value={fullName}
//                 onChange={(e) => setFullName(e.target.value)}
//                 required
//               />
//             </div>
            
//             {/* Email */}
//             <div>
//               <label
//                 htmlFor="email"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 Admin Email
//               </label>
//               <input
//                 type="email"
//                 id="email"
//                 placeholder="admin@example.com"
//                 className={inputClass}
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 required
//               />
//             </div>
            
//             {/* --- REMOVED: Password --- */}
            
//             {/* Assign to Org */}
//             <div>
//               <label
//                 htmlFor="adminOrgId"
//                 className="block text-sm font-medium text-gray-700 dark:text-gray-300"
//               >
//                 Assign to Organization
//               </label>
//               <select
//                 id="adminOrgId"
//                 value={orgId}
//                 onChange={(e) => setOrgId(e.target.value)}
//                 className={inputClass}
//                 required
//               >
//                 <option value="">Select Organization</option>
//                 {orgs.map((o) => (
//                   <option key={o.id} value={o.id}>
//                     {o.name}
//                   </option>
//                 ))}
//               </select>
//             </div>
//             <button
//               type="submit"
//               disabled={adminLoading}
//               className={buttonClass("green", adminLoading)}
//             >
//               {adminLoading ? "Creating..." : "Create Admin"}
//             </button>
//           </form>
//         </div>
//       </div>

//       {/* --- Card 3: Organizations List --- */}
//       <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
//         <div className="p-6">
//           <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
//             Organizations
//           </h2>
//         </div>
//         <div className="overflow-x-auto">
//           <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
//             <thead className="bg-gray-50 dark:bg-gray-700">
//               <tr>
//                 <th
//                   scope="col"
//                   className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
//                 >
//                   Name
//                 </th>
//                 <th
//                   scope="col"
//                   className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
//                 >
//                   Type
//                 </th>
                
//                 {/* --- NEW: Table Columns --- */}
//                 <th
//                   scope="col"
//                   className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
//                 >
//                   City
//                 </th>
//                 <th
//                   scope="col"
//                   className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
//                 >
//                   State
//                 </th>
//                 <th
//                   scope="col"
//                   className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
//                 >
//                   Organization ID
//                 </th>
//               </tr>
//             </thead>
//             <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
//               {orgs.length > 0 ? (
//                 orgs.map((o) => (
//                   <tr key={o.id}>
//                     <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
//                       {o.name}
//                     </td>
//                     <td className="px-6 py-4 whitespace-nowPrap text-sm text-gray-500 dark:text-gray-300">
//                       {o.org_type}
//                     </td>
//                     {/* --- NEW: Table Data --- */}
//                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
//                       {o.city}
//                     </td>
//                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
//                       {o.state}
//                     </td>
//                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300 font-mono">
//                       {o.id}
//                     </td>
//                   </tr>
//                 ))
//               ) : (
//                 <tr>
//                   <td
//                     colSpan="5" // Updated colSpan
//                     className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400"
//                   >
//                     No organizations found.
//                   </td>
//                 </tr>
//               )}
//             </tbody>
//           </table>
//         </div>
//       </div>
//     </Layout>
//   );
// }