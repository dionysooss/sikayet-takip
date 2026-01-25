import { initializeApp } from 'firebase/app';
import { getFirestore, collection, doc, setDoc, query, where, getDocs } from 'firebase/firestore';

// Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyBEPqYXhJDxjRxSRdPJBqWJYGHvgLQvwQI",
    authDomain: "isparta-petrol-crm.firebaseapp.com",
    projectId: "isparta-petrol-crm",
    storageBucket: "isparta-petrol-crm.firebasestorage.app",
    messagingSenderId: "1056906093826",
    appId: "1:1056906093826:web:b0e0e8e3e8e3e8e3e8e3e8"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// SHA-256 hash function
async function hashPassword(password: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

async function createAdminUser() {
    try {
        console.log('🔄 Admin kullanıcısı oluşturuluyor...');

        // Şifreyi hashle
        const hashedPassword = await hashPassword('Dionysos.1881');

        // Kullanıcı adının benzersiz olduğunu kontrol et
        const usersRef = collection(db, 'users');
        const q = query(usersRef, where('username', '==', 'devran'));
        const querySnapshot = await getDocs(q);

        if (!querySnapshot.empty) {
            console.log('⚠️  "devran" kullanıcı adı zaten mevcut, güncelleniyor...');
            const existingDoc = querySnapshot.docs[0];
            await setDoc(doc(db, 'users', existingDoc.id), {
                username: 'devran',
                password: hashedPassword,
                fullName: 'Devran Deveci',
                role: 'admin',
                branch: 'Merkez',
                phone: '+905554443322',
                photoURL: 'https://ui-avatars.com/api/?name=Devran+Deveci&background=random',
                createdAt: new Date(),
                lastLogin: null
            });
            console.log('✅ Kullanıcı güncellendi!');
        } else {
            // Yeni kullanıcı oluştur
            const newUserRef = doc(collection(db, 'users'));
            await setDoc(newUserRef, {
                username: 'devran',
                password: hashedPassword,
                fullName: 'Devran Deveci',
                role: 'admin',
                branch: 'Merkez',
                phone: '+905554443322',
                photoURL: 'https://ui-avatars.com/api/?name=Devran+Deveci&background=random',
                createdAt: new Date(),
                lastLogin: null
            });
            console.log('✅ Admin kullanıcısı oluşturuldu!');
        }

        console.log('\n🎉 İşlem tamamlandı!');
        console.log('\nGiriş bilgileri:');
        console.log('Kullanıcı Adı: devran');
        console.log('Şifre: Dionysos.1881');

        process.exit(0);
    } catch (error) {
        console.error('❌ Hata:', error);
        process.exit(1);
    }
}

createAdminUser();
