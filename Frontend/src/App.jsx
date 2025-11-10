// import React from "react";
// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import Login from "./pages/Login";
// import Dashboard from "./pages/Dashboard";
// import ClassPage from "./pages/ClassPage";
// import AssignmentPage from "./pages/Assignment";

// function App() {
//   return (
//     <Router>
//       <Routes>
//         <Route path="/" element={<Login />} />
//         <Route path="/dashboard/:userId" element={<Dashboard />} />
//         <Route path="/class/:classId/:userId" element={<ClassPage />} />
//         <Route path="/class/:classId/:userId/assignments/:assignmentId" element={<AssignmentPage />} />
//       </Routes>
//     </Router>
//   );
// }

// export default App;

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Unauthorized from "./pages/Unauthorized";
import NotFound from "./pages/NotFound";
import OwnerDashboard from "./pages/OwnerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import SubTeacherDashboard from "./pages/SubTeacherDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import Departments from "./pages/Departments";
import ImportPage from "./pages/Import";
import Classes from "./pages/ClassPage";
import ClassPage from "./pages/ClassPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Dashboards */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/owner" element={<ProtectedRoute allowed={['owner']}><OwnerDashboard /></ProtectedRoute>} />
          <Route path="/admin/dashboard" element={<ProtectedRoute allowed={['admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/teacher/dashboard" element={<ProtectedRoute allowed={['class_teacher']}><TeacherDashboard /></ProtectedRoute>} />
          <Route path="/subteacher/dashboard" element={<ProtectedRoute allowed={['sub_teacher']}><SubTeacherDashboard /></ProtectedRoute>} />
          <Route path="/student/dashboard" element={<ProtectedRoute allowed={['student']}><StudentDashboard /></ProtectedRoute>} />

          {/* Common routes */}
          <Route path="/departments" element={<ProtectedRoute allowed={['admin']}><Departments /></ProtectedRoute>} />
          <Route path="/import" element={<ProtectedRoute allowed={['admin']}><ImportPage /></ProtectedRoute>} />
          <Route path="/classes" element={<ProtectedRoute allowed={['class_teacher','sub_teacher']}><Classes /></ProtectedRoute>} />
          <Route path="/class/:id/*" element={<ProtectedRoute><ClassPage /></ProtectedRoute>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
