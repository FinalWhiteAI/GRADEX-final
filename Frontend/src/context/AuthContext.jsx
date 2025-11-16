// import React, { createContext, useContext, useState, useEffect } from "react";
// import api from "../api/axios";

// const AuthContext = createContext();

// export const AuthProvider = ({ children }) => {
//   const [user, setUser] = useState(null);
//   const [loading, setLoading] = useState(true);

//   const fetchUser = async () => {
//     try {
//       const res = await api.get("/api/users/me");
//       setUser(res.data);
//     } catch (err) {
//       setUser(null);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     const token = localStorage.getItem("token");
//     if (token) fetchUser();
//     else setLoading(false);
//   }, []);

//   const login = async (email, password) => {
//     const res = await api.post("/api/auth/login", { email, password });
//     localStorage.setItem("token", res.session.access_token);
//     await fetchUser();
//   };

//   const logout = () => {
//     localStorage.removeItem("token");
//     setUser(null);
//   };

//   return (
//     <AuthContext.Provider value={{ user, login, logout, loading }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };

// export const useAuth = () => useContext(AuthContext);


import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const res = await api.get("/api/users/me");
      setUser(res.data);
      // FIX 2: Save user to localStorage so Login.js can read it for redirection
      localStorage.setItem("user", JSON.stringify(res.data)); 
    } catch (err) {
      setUser(null);
      localStorage.removeItem("user");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) fetchUser();
    else setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/api/auth/login", { email, password });
    
    // FIX 1: Your backend returns { access_token: "..." }
    // Axios puts the response body inside 'data'.
    const token = res.data.access_token; 
    
    localStorage.setItem("token", token);
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user"); // Clean up user data too
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);


// import React, { useContext, useState, useEffect } from "react";
// import { auth, googleProvider } from "./firebase"; // Import from your config
// import {
//   signInWithPopup, // Only need this
//   signOut,
//   onAuthStateChanged
// } from "firebase/auth";
// import api from "../api/axios"; // Your axios instance

// const AuthContext = React.createContext();

// export function useAuth() {
//   return useContext(AuthContext);
// }

// export function AuthProvider({ children }) {
//   const [currentUser, setCurrentUser] = useState(null);
//   const [loading, setLoading] = useState(true);

//   // This function is still the most important part
//   async function fetchUser(firebaseUser) {
//     if (firebaseUser) {
//       const token = await firebaseUser.getIdToken();
//       api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
//       try {
//         const res = await api.get("/api/users/me");
//         setCurrentUser(res.data);
//         localStorage.setItem("user", JSON.stringify(res.data));
//         return res.data;
//       } catch (err) {
//         console.error("Failed to fetch app user", err);
//         await signOut(auth); 
//         localStorage.clear();
//         api.defaults.headers.common["Authorization"] = null;
//         throw err;
//       }
//     } else {
//       setCurrentUser(null);
//       localStorage.clear();
//       api.defaults.headers.common["Authorization"] = null;
//     }
//   }

//   // DELETED: login(email, password) function

//   // Google login
//   async function loginWithGoogle() {
//     const userCredential = await signInWithPopup(auth, googleProvider);
//     return await fetchUser(userCredential.user);
//   }

//   // Logout function
//   function logout() {
//     localStorage.clear();
//     api.defaults.headers.common["Authorization"] = null;
//     return signOut(auth);
//   }

//   // DELETED: resetPassword(email) function

//   // Listens for auth changes
//   useEffect(() => {
//     const unsubscribe = onAuthStateChanged(auth, (user) => {
//       fetchUser(user).finally(() => setLoading(false));
//     });
//     return unsubscribe;
//   }, []);

//   const value = {
//     currentUser,
//     loginWithGoogle, // Only expose this
//     logout,
//   };

//   return (
//     <AuthContext.Provider value={value}>
//       {!loading && children}
//     </AuthContext.Provider>
//   );
// }