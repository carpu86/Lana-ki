$ErrorActionPreference = "Stop"

$Repo = "C:\Carpuncle Cloud\LanaApp\lana-ki"
$Backend = Join-Path $Repo "backend"
$Frontend = Join-Path $Repo "frontend"
$Python = Join-Path $Repo ".venv\Scripts\python.exe"
$LogDir = Join-Path $Repo "logs\headless"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

function Stop-PortOwner {
    param([int]$Port)
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ -gt 0 } |
        ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

Stop-PortOwner 8030
Stop-PortOwner 5173

$env:LANA_REPO_ROOT = $Repo
$env:LANA_FRONTEND_DIST = Join-Path $Frontend "dist"
$env:LANA_COMMANDER_NAME = "Thomas Heckhoff"
$env:LANA_COMMANDER_CALL = "Commander Thomas"

Start-Process -FilePath $Python -ArgumentList @("-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8030") -WorkingDirectory $Backend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "backend-$Stamp.out.log") -RedirectStandardError (Join-Path $LogDir "backend-$Stamp.err.log")

Start-Sleep -Seconds 6
Start-Process "http://127.0.0.1:8030"
