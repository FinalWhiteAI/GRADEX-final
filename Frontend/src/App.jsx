import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ClassPage from "./pages/ClassPage";
import AssignmentPage from "./pages/Assignment";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard/:userId" element={<Dashboard />} />
        <Route path="/class/:classId/:userId" element={<ClassPage />} />
        <Route path="/class/:classId/:userId/assignments/:assignmentId" element={<AssignmentPage />} />
      </Routes>
    </Router>
  );
}

export default App;
