// SHA-256 hash hesaplama
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function main() {
    const password = 'admin123';
    const hash = await hashPassword(password);
    console.log('\n=== ŞİFRE HASH BİLGİSİ ===\n');
    console.log('Şifre:', password);
    console.log('SHA-256 Hash:', hash);
    console.log('\n📋 Firebase Console\'da password alanına bu hash\'i yapıştırın:\n');
    console.log(hash);
    console.log('\n');
}

main();
