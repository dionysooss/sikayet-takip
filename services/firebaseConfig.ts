import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration from environment variables
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyBaLvaB5XdJ1dkdpjm2c7TTfCp1uTidvA",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "isparta-petrol-crm.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "isparta-petrol-crm",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "750142784638",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:750142784638:web:a99147a47497bef0b1842f",
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-QEQZl5SH3L"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

export default app;
