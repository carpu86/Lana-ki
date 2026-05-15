[CmdletBinding()]
param(
    [string]$RepoRoot = "C:\Carpuncle Cloud\Lana KI\Lana Git",
    [string]$EnvPath = "C:\Carpuncle Cloud\Lana KI\.env"
)

$ErrorActionPreference = 'Stop'
$Timestamp = Get-Date -Format 'yyyyMMddTHHmmssZ'

function Write-Log {
    param([string]$Message)
    $logRoot = $env:LANA_LOG_ROOT
    if ([string]::IsNullOrWhiteSpace($logRoot)) {
        $logRoot = "C:\Carpuncle Cloud\Lana KI\logs"
    }
    New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
    $line = "$(Get-Date -Format o) | $Message"
    $line | Tee-Object -FilePath (Join-Path $logRoot 'lana_self_provision.log') -Append
}

function Backup-File {
    param([string]$Path)
    if (Test-Path $Path) {
        $backupRoot = $env:LANA_BACKUP_ROOT
        if ([string]::IsNullOrWhiteSpace($backupRoot)) {
            $backupRoot = "C:\Carpuncle Cloud\Lana KI\_backups"
        }
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        $destination = Join-Path $backupRoot ((Split-Path $Path -Leaf) + ".${Timestamp}.bak")
        Copy-Item $Path $destination -Force
        Write-Log "Backup erstellt: $destination"
    }
}

function Read-EnvMap {
    param([string]$Path)
    $map = @{}
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^[A-Za-z_][A-Za-z0-9_]*=') {
                $parts = $_ -split '=', 2
                $map[$parts[0]] = $parts[1]
            }
        }
    }
    return $map
}

function Ensure-EnvEntry {
    param([string]$Path, [string]$Key, [string]$Value)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType File -Path $Path | Out-Null
    }
    $current = Read-EnvMap -Path $Path
    if (-not $current.ContainsKey($Key)) {
        Backup-File -Path $Path
        Add-Content -Path $Path -Value "$Key=$Value"
        Write-Log "Env-Eintrag ergänzt: $Key"
    }
}

function Test-TcpPort {
    param([string]$Host, [int]$Port)
    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $task = $client.ConnectAsync($Host, $Port)
        $task.Wait(2000) | Out-Null
        $connected = $client.Connected
        $client.Dispose()
        return $connected
    } catch {
        return $false
    }
}

function Log-PortOwner {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $connection) {
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        Write-Log "Port $Port belegt durch PID $($connection.OwningProcess) / $($process.ProcessName)"
    }
}

Ensure-EnvEntry -Path $EnvPath -Key 'LANA_API_PORT' -Value '8024'
$envMap = Read-EnvMap -Path $EnvPath
foreach ($entry in $envMap.GetEnumerator()) {
    Set-Item -Path "Env:$($entry.Key)" -Value $entry.Value
}

Write-Log "Prüfe LM Studio und ComfyUI"
Write-Log "LM Studio erreichbar: $(Test-TcpPort -Host '127.0.0.1' -Port 1234)"
Write-Log "ComfyUI erreichbar: $(Test-TcpPort -Host '127.0.0.1' -Port 8188)"
Log-PortOwner -Port 8024

$backendLog = Join-Path ($env:LANA_LOG_ROOT ?? 'C:\Carpuncle Cloud\Lana KI\logs') 'lana_uvicorn.log'
$command = "Set-Location '$RepoRoot'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8024"
Start-Process -FilePath 'pwsh' -ArgumentList '-NoLogo','-NoProfile','-Command', $command -RedirectStandardOutput $backendLog -RedirectStandardError $backendLog -WindowStyle Hidden
Write-Log "Backend-Start ausgelöst. Logs: $backendLog"
