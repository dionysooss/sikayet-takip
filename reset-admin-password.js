// Admin şifresini sıfırlama scripti
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, query, where, getDocs, updateDoc, doc } from 'firebase/firestore';

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

// SHA-256 hash fonksiyonu
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function resetAdminPassword() {
    try {
        // Yeni şifre: admin123
        const newPassword = 'admin123';
        const hashedPassword = await hashPassword(newPassword);

        console.log('\n🔐 Admin şifresi sıfırlanıyor...\n');

        // Admin kullanıcısını bul
        const usersRef = collection(db, 'users');
        const q = query(usersRef, where('username', '==', 'devran'));
        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            console.log('❌ Admin kullanıcısı bulunamadı!');
            return;
        }

        const userDoc = querySnapshot.docs[0];

        // Şifreyi güncelle
        await updateDoc(doc(db, 'users', userDoc.id), {
            password: hashedPassword
        });

        console.log('✅ Admin şifresi başarıyla sıfırlandı!');
        console.log('\n📋 Giriş Bilgileri:');
        console.log('   Kullanıcı Adı: devran');
        console.log('   Yeni Şifre: admin123');
        console.log('\n');

    } catch (error) {
        console.error('❌ Hata:', error);
    }
}

resetAdminPassword();
