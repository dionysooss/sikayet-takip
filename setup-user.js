// Firestore'daki tüm kullanıcıları sil ve tek admin kullanıcı oluştur
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs, deleteDoc, doc, setDoc } from 'firebase/firestore';

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

async function setupUser() {
    try {
        console.log('\n🔄 Kullanıcı kurulumu başlıyor...\n');

        // 1. Tüm mevcut kullanıcıları sil
        console.log('📋 Mevcut kullanıcılar siliniyor...');
        const usersSnapshot = await getDocs(collection(db, 'users'));
        let deletedCount = 0;

        for (const userDoc of usersSnapshot.docs) {
            await deleteDoc(doc(db, 'users', userDoc.id));
            deletedCount++;
            console.log(`   ✓ Silindi: ${userDoc.data().username}`);
        }

        console.log(`\n✅ ${deletedCount} kullanıcı silindi\n`);

        // 2. Şifreyi hash'le
        const password = 'Dionysos.1881';
        const hashedPassword = await hashPassword(password);

        console.log('🔐 Şifre hash\'leniyor...');
        console.log(`   Hash: ${hashedPassword}\n`);

        // 3. Yeni admin kullanıcı oluştur
        console.log('👤 Yeni admin kullanıcı oluşturuluyor...');

        const newUser = {
            username: 'devran',
            fullName: 'Devran Kadıköylü',
            password: hashedPassword,
            role: 'admin',
            phone: '+90 (545) 639 32 20',
            phoneRaw: '5456393220',
            phoneCountryCode: 'TR',
            email: '',
            branch: '',
            createdAt: new Date(),
            lastLogin: null
        };

        // Sabit ID kullan
        await setDoc(doc(db, 'users', 'admin-devran'), newUser);

        console.log('✅ Admin kullanıcı oluşturuldu!\n');
        console.log('═══════════════════════════════════════');
        console.log('📋 GİRİŞ BİLGİLERİ');
        console.log('═══════════════════════════════════════');
        console.log('Kullanıcı Adı: devran');
        console.log('Şifre: Dionysos.1881');
        console.log('Tam Ad: Devran Kadıköylü');
        console.log('Telefon: 545 639 3220');
        console.log('Rol: admin');
        console.log('═══════════════════════════════════════\n');

        console.log('✅ Kurulum tamamlandı!\n');

    } catch (error) {
        console.error('❌ HATA:', error);
        process.exit(1);
    }
}

setupUser();
