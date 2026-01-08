import { initializeApp } from 'firebase/app';
import { getFirestore, doc, setDoc } from 'firebase/firestore';
import bcrypt from 'bcryptjs';

// Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyBaLvaB5XdJ1dkdpjm2c7TTfCp1uTidvA",
    authDomain: "isparta-petrol-crm.firebaseapp.com",
    projectId: "isparta-petrol-crm",
    storageBucket: "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: "750142784638",
    appId: "1:750142784638:web:a99147a47497bef0b1842f",
    measurementId: "G-QEQZl5SH3L"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function createAdminUser() {
    try {
        // Yeni şifreyi hash'le
        const password = 'Admin123!'; // Güçlü şifre
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        const adminUser = {
            id: 'admin-' + Date.now(),
            username: 'admin',
            password: hashedPassword,
            fullName: 'Sistem Yöneticisi',
            role: 'ADMIN',
            phone: '+90 (555) 000 00 01',
            phoneRaw: '5550000001',
            phoneCountryCode: 'TR',
            email: 'admin@ispartapetrol.com',
            branch: 'Merkez'
        };

        await setDoc(doc(db, 'users', adminUser.id), adminUser);

        console.log('✅ Admin kullanıcı oluşturuldu!');
        console.log('Kullanıcı Adı: admin');
        console.log('Şifre: Admin123!');
        console.log('\nBu bilgileri not alın ve ilk girişten sonra şifrenizi değiştirin!');

        process.exit(0);
    } catch (error) {
        console.error('❌ Hata:', error);
        process.exit(1);
    }
}

createAdminUser();
