# Vercel API ile Environment Variables Ekleme
# Project ID
$projectId = "prj_gAJFedQ2ov6RqS2Cc2W78K0pEaMJ"

# Vercel token'ı al
$authFile = "$env:USERPROFILE\.vercel\auth.json"
if (Test-Path $authFile) {
    $auth = Get-Content $authFile | ConvertFrom-Json
    $token = $auth.token
}
else {
    Write-Host "❌ Vercel token bulunamadı!" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Vercel API ile environment variables ekleniyor...`n" -ForegroundColor Green

# Environment variables
$envVars = @(
    @{key = "VITE_FIREBASE_API_KEY"; value = "AIzaSyBaLvaB5XdJ1dkdpjm2c7TTEfCp1uTidvA" },
    @{key = "VITE_FIREBASE_AUTH_DOMAIN"; value = "isparta-petrol-crm.firebaseapp.com" },
    @{key = "VITE_FIREBASE_PROJECT_ID"; value = "isparta-petrol-crm" },
    @{key = "VITE_FIREBASE_STORAGE_BUCKET"; value = "isparta-petrol-crm.firebasestorage.app" },
    @{key = "VITE_FIREBASE_MESSAGING_SENDER_ID"; value = "750142784638" },
    @{key = "VITE_FIREBASE_APP_ID"; value = "1:750142784638:web:a99147a47497bef0b1842f" },
    @{key = "VITE_GOOGLE_AI_API_KEY"; value = "AIzaSyCyJQc9PwpJjPZETzXqtSWZG9FOnch3flE" }
)

$count = 0
foreach ($env in $envVars) {
    $count++
    Write-Host "[$count/7] $($env.key) ekleniyor..." -ForegroundColor Cyan
    
    $body = @{
        key    = $env.key
        value  = $env.value
        type   = "encrypted"
        target = @("production")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.vercel.com/v10/projects/$projectId/env" `
            -Method POST `
            -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type"  = "application/json"
        } `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "  ✅ Başarılı!" -ForegroundColor Green
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 409) {
            Write-Host "  ⚠️  Zaten var (atlanıyor)" -ForegroundColor Yellow
        }
        else {
            Write-Host "  ❌ Hata: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host "`n🎉 Environment variables eklendi!" -ForegroundColor Green
Write-Host "🔄 Redeploy yapılıyor...`n" -ForegroundColor Cyan

# Redeploy
vercel --prod --yes

Write-Host "`n✅ Tamamlandı!" -ForegroundColor Green
Write-Host "🌐 URL: https://isparta-petrol-sikayet-takip.vercel.app" -ForegroundColor Cyan
