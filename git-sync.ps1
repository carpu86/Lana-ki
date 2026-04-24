# =================================================================
# CARPUNCLE CLOUD - GITHUB SYNC HELPER
# =================================================================
param(
    [string]$Action = "menu",
    [string]$Message = ""
)

$BasePath = "C:\Carpuncle Cloud\LanaApp"
$BackupPath = "Z:\CarpuncleCloud\Backups"
Set-Location $BasePath

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          GITHUB SYNC - LANAAPP                       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  📦 Repository: https://github.com/carpu86/Lanaapp.git" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  1️⃣  Status anzeigen (git status)" -ForegroundColor Green
    Write-Host "  2️⃣  Änderungen hochladen (commit + push)" -ForegroundColor Green
    Write-Host "  3️⃣  Änderungen herunterladen (pull)" -ForegroundColor Green
    Write-Host "  4️⃣  Backup erstellen" -ForegroundColor Green
    Write-Host "  5️⃣  Letzte Commits anzeigen" -ForegroundColor Green
    Write-Host "  6️⃣  Alle Dateien hinzufügen (git add .)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Q️⃣  Beenden" -ForegroundColor Red
    Write-Host ""
    
    $choice = Read-Host "Wähle eine Option"
    
    switch ($choice) {
        "1" { 
            Write-Host "`n📊 Git Status:" -ForegroundColor Cyan
            git status
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "2" {
            Write-Host "`n📤 Änderungen werden hochgeladen..." -ForegroundColor Cyan
            
            # Backup erstellen
            $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
            $backupDir = "$BackupPath\LanaApp_$timestamp"
            
            if (Test-Path "Z:\") {
                New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
                Copy-Item "$BasePath\*" -Destination $backupDir -Recurse -Force -Exclude @('node_modules','.git','venv')
                Write-Host "✅ Backup erstellt: $backupDir" -ForegroundColor Green
            }
            
            # Git add
            git add .
            
            # Commit Message
            $msg = Read-Host "Commit-Message (Enter für auto-Message)"
            if (-not $msg) {
                $msg = "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            }
            
            git commit -m $msg
            
            # Push
            Write-Host "`n🚀 Pushe zu GitHub..." -ForegroundColor Yellow
            git push -u origin main 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Erfolgreich hochgeladen!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Push fehlgeschlagen. Prüfe GitHub-Zugangsdaten!" -ForegroundColor Red
                Write-Host "💡 Eventuell musst du dich bei GitHub anmelden:" -ForegroundColor Yellow
                Write-Host "   gh auth login" -ForegroundColor White
            }
            
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "3" {
            Write-Host "`n📥 Hole Änderungen von GitHub..." -ForegroundColor Cyan
            git pull origin main
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Erfolgreich synchronisiert!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Pull fehlgeschlagen!" -ForegroundColor Red
            }
            
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "4" {
            Write-Host "`n💾 Erstelle Backup..." -ForegroundColor Cyan
            $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
            $backupDir = "$BackupPath\LanaApp_$timestamp"
            
            if (Test-Path "Z:\") {
                New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
                Copy-Item "$BasePath\*" -Destination $backupDir -Recurse -Force -Exclude @('node_modules','.git','venv')
                Write-Host "✅ Backup erstellt: $backupDir" -ForegroundColor Green
            } else {
                Write-Host "❌ Z:\ nicht verfügbar!" -ForegroundColor Red
            }
            
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "5" {
            Write-Host "`n📜 Letzte Commits:" -ForegroundColor Cyan
            git log --oneline -10
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "6" {
            Write-Host "`n➕ Füge alle Dateien hinzu..." -ForegroundColor Cyan
            git add .
            Write-Host "✅ Alle Dateien staged" -ForegroundColor Green
            Read-Host "`nEnter drücken"
            Show-Menu
        }
        "q" { 
            Write-Host "`n👋 Bis bald!" -ForegroundColor Cyan
            exit 
        }
        default { 
            Write-Host "❌ Ungültige Eingabe!" -ForegroundColor Red
            Start-Sleep -Seconds 1
            Show-Menu 
        }
    }
}

# Hauptlogik
if ($Action -eq "menu") {
    Show-Menu
} elseif ($Action -eq "push") {
    git add .
    if ($Message) {
        git commit -m $Message
    } else {
        git commit -m "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    git push -u origin main
} elseif ($Action -eq "pull") {
    git pull origin main
} elseif ($Action -eq "status") {
    git status
}
