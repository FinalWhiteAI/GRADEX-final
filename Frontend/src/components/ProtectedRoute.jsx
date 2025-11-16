import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowed }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="p-6 text-center">Loading...</div>;
  if (!user) return <Navigate to="/" />;
  
  const roles = user.roles || [];
  if (!allowed || allowed.some((r) => roles.includes(r))) return children;

  return <Navigate to="/unauthorized" />;
}

// ProtectedRoute.jsx

// import { Navigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

// export default function ProtectedRoute({ children, allowed }) {
//  // FIX 1: Change 'user' to 'currentUser'
//  const { currentUser, loading } = useAuth();
//  if (loading) return <div className="p-6 text-center">Loading...</div>;
 
//  // FIX 2: Change 'user' to 'currentUser'
//  if (!currentUser) return <Navigate to="/" />;
 
//  // FIX 3: Change 'user' to 'currentUser'
//  const roles = currentUser.roles || [];
//  if (!allowed || allowed.some((r) => roles.includes(r))) return children;
//  return <Navigate to="/unauthorized" />;
// }