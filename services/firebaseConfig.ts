import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBaLvaB5XdJ1dkdpjm2c7TTEfCp1uTidvA",
    authDomain: "isparta-petrol-crm.firebaseapp.com",
    projectId: "isparta-petrol-crm",
    storageBucket: "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: "750142784638",
    appId: "1:750142784638:web:a99147a47497bef0b1842f",
    measurementId: "G-QEQZl5SH3L"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

// Initialize Firebase Authentication
export const auth = getAuth(app);

export default app;
