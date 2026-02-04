const https = require('https');
const { execSync } = require('child_process');

// Get Vercel token from auth
let token;
try {
    const authConfig = require('os').homedir() + '/.vercel/auth.json';
    const fs = require('fs');
    if (fs.existsSync(authConfig)) {
        const auth = JSON.parse(fs.readFileSync(authConfig, 'utf8'));
        token = auth.token;
    }
} catch (e) {
    console.error('❌ Vercel token bulunamadı. Önce "vercel login" yapın.');
    process.exit(1);
}

// Get project ID
const projectId = 'prj_gAJFedQ2ov6RqS2Cc2W78K0pEaMJ';

// Environment variables to add
const envVars = [
    { key: 'VITE_FIREBASE_API_KEY', value: 'AIzaSyBaLvaB5XdJ1dkdpjm2c7TTEfCp1uTidvA' },
    { key: 'VITE_FIREBASE_AUTH_DOMAIN', value: 'isparta-petrol-crm.firebaseapp.com' },
    { key: 'VITE_FIREBASE_PROJECT_ID', value: 'isparta-petrol-crm' },
    { key: 'VITE_FIREBASE_STORAGE_BUCKET', value: 'isparta-petrol-crm.firebasestorage.app' },
    { key: 'VITE_FIREBASE_MESSAGING_SENDER_ID', value: '750142784638' },
    { key: 'VITE_FIREBASE_APP_ID', value: '1:750142784638:web:a99147a47497bef0b1842f' },
    { key: 'VITE_GOOGLE_AI_API_KEY', value: 'AIzaSyCyJQc9PwpJjPZETzXqtSWZG9FOnch3flE' }
];

console.log('🚀 Vercel API ile environment variables ekleniyor...\n');

let successCount = 0;
let failCount = 0;

envVars.forEach((envVar, index) => {
    console.log(`[${index + 1}/7] ${envVar.key} ekleniyor...`);

    const data = JSON.stringify({
        key: envVar.key,
        value: envVar.value,
        type: 'encrypted',
        target: ['production']
    });

    const options = {
        hostname: 'api.vercel.com',
        port: 443,
        path: `/v10/projects/${projectId}/env`,
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Content-Length': data.length
        }
    };

    const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
            responseData += chunk;
        });

        res.on('end', () => {
            if (res.statusCode === 200 || res.statusCode === 201) {
                console.log(`  ✅ Başarılı!`);
                successCount++;
            } else if (res.statusCode === 409) {
                console.log(`  ⚠️  Zaten var (atlanıyor)`);
                successCount++;
            } else {
                console.log(`  ❌ Hata: ${res.statusCode}`);
                failCount++;
            }

            // If this is the last one, trigger redeploy
            if (index === envVars.length - 1) {
                setTimeout(() => {
                    console.log(`\n📊 Sonuç: ${successCount} başarılı, ${failCount} hata`);
                    console.log('\n🔄 Redeploy yapılıyor...');
                    try {
                        execSync('vercel --prod --yes', { stdio: 'inherit' });
                        console.log('\n✅ Deployment tamamlandı!');
                        console.log('🌐 URL: https://isparta-petrol-sikayet-takip.vercel.app');
                    } catch (e) {
                        console.error('❌ Redeploy hatası:', e.message);
                    }
                }, 1000);
            }
        });
    });

    req.on('error', (error) => {
        console.log(`  ❌ Bağlantı hatası: ${error.message}`);
        failCount++;
    });

    req.write(data);
    req.end();

    // Wait a bit between requests
    if (index < envVars.length - 1) {
        execSync('timeout /t 1 /nobreak', { stdio: 'ignore' });
    }
});
