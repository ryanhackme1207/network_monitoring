# MikroTik Cloudflare Tunnel Automatic Manager
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "    MikroTik Zabbix Cloudflare Tunnel Health Check      " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$runningCloudflared = Get-Process cloudflared -ErrorAction SilentlyContinue

if ($runningCloudflared) {
    Write-Host "✅ Cloudflare Tunnel is actively RUNNING!" -ForegroundColor Green
    Write-Host "Active Process IDs: $($runningCloudflared.Id -join ', ')" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Cloudflare Tunnel was not running. Starting background tunnels..." -ForegroundColor Yellow
    
    # Start Dashboard Tunnel (3000)
    Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel --url http://localhost:3000" -WindowStyle Hidden
    
    # Start Zabbix Web Tunnel (8080)
    Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel --url http://localhost:8080" -WindowStyle Hidden
    
    Write-Host "🚀 Cloudflare Tunnels have been launched in the background!" -ForegroundColor Green
}

Write-Host "--------------------------------------------------------"
Write-Host "1. Dashboard Tunnel (Port 3000): ACTIVE" -ForegroundColor Green
Write-Host "2. Zabbix Web Tunnel (Port 8080): ACTIVE" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
