$ErrorActionPreference = "Stop"

$Repo     = "C:\Carpuncle Cloud\LanaApp\lana-ki"
$Backend  = Join-Path $Repo "backend"
$Frontend = Join-Path $Repo "frontend"
$Python   = Join-Path $Repo ".venv\Scripts\python.exe"
$LogDir   = Join-Path $Repo "logs\headless"
$Stamp    = Get-Date -Format "yyyyMMdd-HHmmss"

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

Start-Process -FilePath $Python -ArgumentList @("-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8030") -WorkingDirectory $Backend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "backend-$Stamp.out.log") -RedirectStandardError (Join-Path $LogDir "backend-$Stamp.err.log")

Start-Sleep -Seconds 4

$FrontendCmd = 'set "VITE_API_BASE=http://127.0.0.1:8030" && npm run dev -- --host 0.0.0.0 --port 5173'
Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", $FrontendCmd) -WorkingDirectory $Frontend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "frontend-$Stamp.out.log") -RedirectStandardError (Join-Path $LogDir "frontend-$Stamp.err.log")

Start-Sleep -Seconds 6
Start-Process "http://127.0.0.1:5173"
