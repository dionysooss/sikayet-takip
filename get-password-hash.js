// Dionysos.1881 şifresinin hash'ini hesapla
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function main() {
    const password = 'Dionysos.1881';
    const hash = await hashPassword(password);

    console.log('\n═══════════════════════════════════════════════════════════');
    console.log('FİREBASE CONSOLE KULLANICI OLUŞTURMA TALİMATLARI');
    console.log('═══════════════════════════════════════════════════════════\n');

    console.log('1. Firebase Console > Firestore > users koleksiyonu');
    console.log('2. TÜM mevcut kullanıcıları SİL (devran, testuser, vb.)');
    console.log('3. "Add document" butonuna tıkla');
    console.log('4. Document ID: admin-devran');
    console.log('5. Aşağıdaki alanları AYNEN ekle:\n');

    console.log('   username (string): devran');
    console.log('   fullName (string): Devran Kadıköylü');
    console.log('   password (string): ' + hash);
    console.log('   role (string): admin');
    console.log('   phone (string): +90 (545) 639 32 20');
    console.log('   phoneRaw (string): 5456393220');
    console.log('   phoneCountryCode (string): TR');
    console.log('   email (string): (boş bırak)');
    console.log('   branch (string): (boş bırak)');
    console.log('   createdAt (timestamp): (şimdi)');
    console.log('   lastLogin (null): null\n');

    console.log('6. Save butonuna tıkla');
    console.log('7. SADECE 1 kullanıcı olduğunu doğrula\n');

    console.log('═══════════════════════════════════════════════════════════');
    console.log('GİRİŞ BİLGİLERİ (Test için)');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('Kullanıcı Adı: devran');
    console.log('Şifre: Dionysos.1881');
    console.log('═══════════════════════════════════════════════════════════\n');

    console.log('ŞİFRE HASH (kopyala-yapıştır için):');
    console.log(hash);
    console.log('\n');
}

main();
