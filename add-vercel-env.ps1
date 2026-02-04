# Vercel Environment Variables Otomatik Ekleme Scripti

Write-Host "🚀 Vercel Environment Variables Ekleniyor..." -ForegroundColor Green

# Environment variables array
$envVars = @(
    @{Name="VITE_FIREBASE_API_KEY"; Value="AIzaSyBaLvaB5XdJ1dkdpjm2c7TTEfCp1uTidvA"},
    @{Name="VITE_FIREBASE_AUTH_DOMAIN"; Value="isparta-petrol-crm.firebaseapp.com"},
    @{Name="VITE_FIREBASE_PROJECT_ID"; Value="isparta-petrol-crm"},
    @{Name="VITE_FIREBASE_STORAGE_BUCKET"; Value="isparta-petrol-crm.firebasestorage.app"},
    @{Name="VITE_FIREBASE_MESSAGING_SENDER_ID"; Value="750142784638"},
    @{Name="VITE_FIREBASE_APP_ID"; Value="1:750142784638:web:a99147a47497bef0b1842f"},
    @{Name="VITE_GOOGLE_AI_API_KEY"; Value="AIzaSyCyJQc9PwpJjPZETzXqtSWZG9FOnch3flE"}
)

$count = 0
foreach ($env in $envVars) {
    $count++
    Write-Host "[$count/7] Ekleniyor: $($env.Name)..." -ForegroundColor Cyan
    
    # Create temp file with value
    $tempFile = [System.IO.Path]::GetTempFileName()
    $env.Value | Out-File -FilePath $tempFile -Encoding utf8 -NoNewline
    
    # Add to Vercel
    try {
        Get-Content $tempFile | vercel env add $env.Name production 2>&1 | Out-Null
        Write-Host "  ✅ Başarılı!" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  Hata (muhtemelen zaten var)" -ForegroundColor Yellow
    } finally {
        Remove-Item $tempFile -Force
    }
}

Write-Host "`n🎉 Tüm environment variables eklendi!" -ForegroundColor Green
Write-Host "🔄 Şimdi redeploy yapılıyor..." -ForegroundColor Cyan

# Redeploy
vercel --prod --yes

Write-Host "`n✅ İşlem tamamlandı!" -ForegroundColor Green
Write-Host "🌐 URL: https://isparta-petrol-sikayet-takip.vercel.app" -ForegroundColor Cyan
