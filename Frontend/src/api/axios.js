// import { createClient } from "@supabase/supabase-js";
// import axios from "axios";

// export const supabase = createClient(
//   import.meta.env.VITE_SUPABASE_URL,
//   import.meta.env.VITE_SUPABASE_KEY
// );

// export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

// export const api = axios.create({
//   baseURL: BACKEND_URL,
// });

import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

