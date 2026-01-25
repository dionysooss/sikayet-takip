// OTOMATIK KURULUM - Tek admin kullanıcı oluştur
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

async function setupUser() {
    try {
        console.log('\n🔄 KULLANICI KURULUMU BAŞLIYOR...\n');

        // 1. Tüm mevcut kullanıcıları sil
        console.log('🗑️  Mevcut kullanıcılar siliniyor...');
        const usersSnapshot = await getDocs(collection(db, 'users'));

        for (const userDoc of usersSnapshot.docs) {
            await deleteDoc(doc(db, 'users', userDoc.id));
            console.log(`   ✓ Silindi: ${userDoc.data().username || userDoc.id}`);
        }

        console.log(`✅ ${usersSnapshot.size} kullanıcı silindi\n`);

        // 2. Yeni admin kullanıcı oluştur
        console.log('👤 Admin kullanıcı oluşturuluyor...\n');

        const passwordHash = '6fcb5c9c72f05cbcf4313a1f53a553bd7ccb36c23816a36907e8783ca1709a75';

        const adminUser = {
            username: 'devran',
            fullName: 'Devran Kadıköylü',
            password: passwordHash,
            role: 'admin',
            phone: '+90 (545) 639 32 20',
            phoneRaw: '5456393220',
            phoneCountryCode: 'TR',
            email: '',
            branch: '',
            createdAt: new Date(),
            lastLogin: null
        };

        await setDoc(doc(db, 'users', 'admin-devran'), adminUser);

        console.log('✅ Admin kullanıcı oluşturuldu!\n');

        // 3. Doğrulama
        console.log('🔍 Doğrulama yapılıyor...');
        const finalUsers = await getDocs(collection(db, 'users'));
        console.log(`   Toplam kullanıcı sayısı: ${finalUsers.size}`);

        finalUsers.forEach(doc => {
            const user = doc.data();
            console.log(`   ✓ ${user.username} (${user.fullName}) - ${user.role}`);
        });

        console.log('\n═══════════════════════════════════════════════════════════');
        console.log('✅ KURULUM TAMAMLANDI!');
        console.log('═══════════════════════════════════════════════════════════');
        console.log('📋 GİRİŞ BİLGİLERİ:');
        console.log('   Kullanıcı Adı: devran');
        console.log('   Şifre: Dionysos.1881');
        console.log('   Tam Ad: Devran Kadıköylü');
        console.log('   Telefon: 545 639 3220');
        console.log('   Rol: admin');
        console.log('═══════════════════════════════════════════════════════════\n');

        console.log('⚠️  ŞİMDİ FIRESTORE RULES\'U GÜVENLİ HALE GETİRİN!\n');

    } catch (error) {
        console.error('\n❌ HATA:', error.message);
        console.error('Detay:', error);
        process.exit(1);
    }
}

setupUser();
