# Masaüstü Kısayolu Oluşturma

## Manuel Yöntem (En Kolay)

1. **Sikayet_Takip.bat** dosyasına sağ tıklayın
2. **"Kısayol oluştur"** seçin
3. Oluşan kısayolu **Masaüstü**'ne taşıyın
4. İsterseniz adını değiştirin: **"Şikayet Takip Sistemi"**

## Otomatik Yöntem

Aşağıdaki komutu PowerShell'de çalıştırın:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Sikayet_Takip.lnk")
$Shortcut.TargetPath = "C:\Users\devra\OneDrive\Desktop\ŞİKAYET TAKİP SİSTEMİ\Sikayet_Takip.bat"
$Shortcut.WorkingDirectory = "C:\Users\devra\OneDrive\Desktop\ŞİKAYET TAKİP SİSTEMİ"
$Shortcut.Save()
```

## Kullanım

Masaüstündeki kısayola çift tıklayın → Uygulama açılır!

✅ **Sikayet_Takip.bat** dosyası hazır!
