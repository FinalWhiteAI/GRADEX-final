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
