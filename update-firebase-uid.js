// Firestore'daki kullanıcıya firebaseUid ekle
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
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

async function updateFirebaseUid() {
    try {
        console.log('\n🔄 Firestore firebaseUid güncelleniyor...\n');

        // 1. Firestore'dan kullanıcıyı al
        const userDoc = await getDoc(doc(db, 'users', 'ZaM9MhviYOZ4vfqQSFbr'));
        const userData = userDoc.data();

        // 2. Firebase Auth ile giriş yap
        const email = `${userData.username}@ispartapetrol.internal`;
        const password = 'Dionysos.1881';

        console.log(`📋 Giriş yapılıyor: ${email}`);
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log(`✓ Giriş başarılı: ${userCredential.user.uid}`);

        // 3. Firestore'u güncelle
        console.log('\n📝 Firestore güncelleniyor...');
        await updateDoc(doc(db, 'users', 'ZaM9MhviYOZ4vfqQSFbr'), {
            email: email,
            firebaseUid: userCredential.user.uid
        });

        console.log('\n✅ TAMAMLANDI!');
        console.log(`Firebase UID: ${userCredential.user.uid}`);
        console.log('\nŞimdi uygulamadan giriş yapabilirsiniz:');
        console.log('  Kullanıcı Adı: devran');
        console.log('  Şifre: Dionysos.1881\n');

    } catch (error) {
        console.error('\n❌ HATA:', error.message);
    }
}

updateFirebaseUid();
