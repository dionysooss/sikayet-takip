// Firebase Authentication Migration Script
// Mevcut kullanıcıyı Firebase Auth'a ekler (gizli email ile)

import { initializeApp } from 'firebase/app';
import { getAuth, createUserWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, doc, updateDoc, getDoc } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyBaLvaB5XdJ1dkdpjm2c7TTEfCp1uTidvA",
    authDomain: "isparta-petrol-crm.firebaseapp.com",
    projectId: "isparta-petrol-crm",
    storageBucket: "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: "750142784638",
    appId: "1:750142784638:web:a99147a47497bef0b1842f"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

async function migrateUser() {
    try {
        console.log('\n🔄 Firebase Authentication Migration Başlıyor...\n');

        // 1. Firestore'dan mevcut kullanıcıyı bul
        console.log('📋 Firestore\'dan kullanıcı bilgileri alınıyor...');
        const userDoc = await getDoc(doc(db, 'users', 'ZaM9MhviYOZ4vfqQSFbr'));

        if (!userDoc.exists()) {
            console.error('❌ Kullanıcı bulunamadı!');
            return;
        }

        const userData = userDoc.data();
        console.log(`   ✓ Kullanıcı bulundu: ${userData.username} (${userData.fullName})`);

        // 2. Otomatik email oluştur (gizli, kullanıcı görmeyecek)
        const email = `${userData.username}@ispartapetrol.internal`;
        const password = 'Dionysos.1881';

        console.log('\n🔐 Firebase Authentication hesabı oluşturuluyor...');
        console.log(`   Username: ${userData.username}`);
        console.log(`   Email (gizli): ${email}`);

        // 3. Firebase Auth hesabı oluştur
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log(`   ✓ Firebase Auth hesabı oluşturuldu: ${userCredential.user.uid}`);

        // 4. Firestore document'i güncelle
        console.log('\n📝 Firestore document güncelleniyor...');
        await updateDoc(doc(db, 'users', 'ZaM9MhviYOZ4vfqQSFbr'), {
            email: email,
            firebaseUid: userCredential.user.uid
        });
        console.log('   ✓ Firestore güncellendi');

        console.log('\n═══════════════════════════════════════════════════════════');
        console.log('✅ MIGRATION TAMAMLANDI!');
        console.log('═══════════════════════════════════════════════════════════');
        console.log('📋 Giriş Bilgileri (KULLANICI İÇİN):');
        console.log(`   Kullanıcı Adı: ${userData.username}`);
        console.log(`   Şifre: ${password}`);
        console.log('\n📋 Teknik Bilgiler (BACKEND):');
        console.log(`   Email (gizli): ${email}`);
        console.log(`   Firebase UID: ${userCredential.user.uid}`);
        console.log('═══════════════════════════════════════════════════════════\n');

    } catch (error) {
        console.error('\n❌ HATA:', error.message);
        if (error.code === 'auth/email-already-in-use') {
            console.log('\n⚠️  Bu email zaten kullanımda. Firebase Console\'dan kontrol edin.');
        }
    }
}

migrateUser();
