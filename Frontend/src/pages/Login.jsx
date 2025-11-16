

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // 1. Wait for login and fetchUser to complete
      await login(email, password);
      
      // 2. Retrieve the user data stored by fetchUser (in AuthContext fix)
      const storedUser = localStorage.getItem("user");
      const user = storedUser ? JSON.parse(storedUser) : null;

      // 3. Role-based Redirect
      if (user?.roles?.includes("owner")) navigate("/owner");
      else if (user?.roles?.includes("admin")) navigate("/admin/dashboard");
      else if (user?.roles?.includes("class_teacher")) navigate("/teacher/dashboard");
      else if (user?.roles?.includes("sub_teacher")) navigate("/subteacher/dashboard");
      else if (user?.roles?.includes("student")) navigate("/student/dashboard");
      else navigate("/dashboard"); 
      
    } catch (err) {
      console.error(err);
      // Handle specific error from backend if available
      const msg = err.response?.data?.detail || "Invalid credentials. Try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-4 text-center dark:text-white">Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            className="w-full px-4 py-2 border rounded-md dark:bg-gray-700 dark:text-white"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            className="w-full px-4 py-2 border rounded-md dark:bg-gray-700 dark:text-white"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
          {error && <p className="text-red-500 text-center text-sm">{error}</p>}
        </form>
      </div>
    </div>
  );
}

// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

// // A simple SVG for the Google G logo
// const GoogleIcon = () => (
//   <svg className="w-5 h-5" viewBox="0 0 48 48">
//     <path fill="#4285F4" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l8.06 6.25C12.7 13.45 18.04 9.5 24 9.5z"></path>
//     <path fill="#34A853" d="M46.98 24.55c0-1.57-.15-3.09-.42-4.55H24v8.51h12.8c-.57 2.73-2.2 5.08-4.64 6.69l7.35 5.71C44.49 37.07 46.98 31.25 46.98 24.55z"></path>
//     <path fill="#FBBC05" d="M10.6 28.71c-.35-.99-.54-2.04-.54-3.13s.19-2.14.54-3.13l-8.06-6.25C.92 18.25 0 21.05 0 24s.92 5.75 2.56 7.94l8.04-6.23z"></path>
//     <path fill="#EA4335" d="M24 48c6.47 0 11.9-2.13 15.84-5.75l-7.35-5.71c-2.11 1.42-4.79 2.27-7.49 2.27-5.96 0-11.3-3.95-13.14-9.28L2.56 35.78C6.51 43.62 14.62 48 24 48z"></path>
//     <path fill="none" d="M0 0h48v48H0z"></path>
//   </svg>
// );

// export default function Login() {
//   // Get the user, loading state, and login function from context
//   // At the top of your Login function
// const { currentUser, loading, loginWithGoogle } = useAuth();
//   const navigate = useNavigate();

//   // Local state for button loading and error messages
//   const [isLoggingIn, setIsLoggingIn] = useState(false);
//   const [error, setError] = useState("");

//   // --- THIS IS THE CRITICAL CHANGE ---
//   // This effect runs when the component loads AND when the 'user' or 'loading'
//   // state from your AuthContext changes.
//   // In Login.jsx
// useEffect(() => {
//     if (loading) {
//       return; // Wait until auth is ready
//     }

//     if (currentUser) {
//       const roles = currentUser.roles || [];

//       // 1. Check for specific single roles
//       if (roles.length === 1) {
//         if (roles.includes("owner")) return navigate("/owner");
//         if (roles.includes("admin")) return navigate("/admin/dashboard");
//         if (roles.includes("hod")) return navigate("/hod-dashboard");
//         if (roles.includes("class_teacher")) return navigate("/teacher-dashboard");
//         if (roles.includes("student")) return navigate("/student-dashboard");
//         // Add other single roles here
//       }
      
//       // 2. If they have 0 roles or MORE than 1 role, send to portal
//       if (roles.length > 1) {
//          return navigate("/portal"); // <-- THE NEW PORTAL PAGE
//       }

//       // 3. Fallback / User has no roles
//       return navigate("/dashboard"); 
//     }
//   }, [currentUser, loading, navigate]);
  
//   const handleGoogleLogin = async () => {
//     setError("");
//     setIsLoggingIn(true); // Use local loading state
//     try {
//       // This will trigger the redirect. The code
//       // *after* this will not run.
//       await loginWithGoogle();
//        setIsLoggingIn(false); 
       
//       // The page will navigate away, so we don't do anything else here.
//       // The useEffect hook will handle the success *after* redirect.

//     } catch (err) {
//       console.error(err);
//       const msg = err.code || "Failed to sign in. Try again.";
//       setError(msg.replace("auth/", "").replace(/-/g, " "));
//       setIsLoggingIn(false); // Only set to false on error
//     }
//   };

//   // While AuthContext is loading, show a generic loading screen
//   // This also hides the login button while the redirect is processing
//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
//         <p className="dark:text-white">Loading session...</p>
//       </div>
//     );
//   }

//   // If we are not loading AND there is no user, show the login page
//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
//       <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-md">
//         <div className="flex justify-center mb-4">
//           <span className="text-6xl" role="img" aria-label="Classroom">
//             🎓
//           </span>
//         </div>
//         <h2 className="text-2xl font-bold mb-4 text-center text-gray-800 dark:text-white">
//           Sign in to your Account
//         </h2>
//         <p className="text-center text-sm text-gray-600 dark:text-gray-400 mb-6">
//           Please sign in with the Google account provided by your administrator.
//         </p>

//         {error && (
//           <p className="text-red-500 text-center text-sm capitalize mb-4">
//             {error}
//           </p>
//         )}

//         {/* Google Sign-in Button */}
//         <button
//           onClick={handleGoogleLogin}
//           disabled={isLoggingIn} // Use local loading state
//           className="w-full flex items-center justify-center gap-3 bg-blue-600 hover:bg-blue-700 text-white py-2.5 border border-blue-600 rounded-lg font-semibold transition-all duration-300 disabled:opacity-50"
//         >
//           <GoogleIcon />
//           {isLoggingIn ? "Signing in..." : "Sign in with Google"}
//         </button>
//       </div>
//     </div>
//   );
// }