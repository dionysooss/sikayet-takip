// Dionysos.1881 için DOĞRU hash hesapla
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
    console.log('DOĞRU ŞİFRE HASH');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('Şifre:', password);
    console.log('Hash:', hash);
    console.log('═══════════════════════════════════════════════════════════\n');
    console.log('Firebase Console\'da password alanını bu hash ile güncelleyin:\n');
    console.log(hash);
    console.log('\n');
}

main();
