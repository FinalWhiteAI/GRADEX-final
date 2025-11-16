import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAxgR84PYsEl5XW9BlR82WlYOvGTEh58qA",
  authDomain: "whiteai-ce125.firebaseapp.com",
  projectId: "whiteai-ce125",
  storageBucket: "whiteai-ce125.firebasestorage.app",
  messagingSenderId: "747941691894",
  appId: "1:747941691894:web:cef6cdfbbaaff8c4e487d7",
  measurementId: "G-WNY2T06K28"
};
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
