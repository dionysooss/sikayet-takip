// Script to check admin user password from Firestore
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyDXvPKkMvPqpwAZIeKxgULHGbFPz0Uu5Uc",
    authDomain: "isparta-petrol-crm.firebaseapp.com",
    projectId: "isparta-petrol-crm",
    storageBucket: "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: "1012476682691",
    appId: "1:1012476682691:web:e4e5a8e9e1d3e4e5e6e7e8"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function checkAdminPassword() {
    try {
        const usersSnapshot = await getDocs(collection(db, 'users'));

        console.log('\n=== KULLANICILAR ===\n');
        usersSnapshot.forEach((doc) => {
            const user = doc.data();
            console.log(`Kullanıcı: ${user.username}`);
            console.log(`Ad Soyad: ${user.fullName}`);
            console.log(`Rol: ${user.role}`);
            console.log(`Şifre (Hash): ${user.password}`);
            console.log('---');
        });
    } catch (error) {
        console.error('Hata:', error);
    }
}

checkAdminPassword();
