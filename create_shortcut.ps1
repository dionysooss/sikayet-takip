$WshShell = New-Object -ComObject WScript.Shell
$TargetPath = Join-Path $PSScriptRoot "Sikayet_Takip.bat"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "Sikayet_Takip.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Sikayet Takip ve Arsivleme Sistemi"
$Shortcut.Save()
Write-Host "Masaustu kisayolu olusturuldu: $ShortcutPath" -ForegroundColor Green
