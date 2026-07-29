# Zabbix Docker Management Script for Windows PowerShell
$DOCKER_BIN = "C:\Users\Acer Nitro 5\AppData\Local\Programs\DockerDesktop\resources\bin"
if (Test-Path $DOCKER_BIN) {
    $env:PATH += ";$DOCKER_BIN"
}

param (
    [Parameter(Position=0)]
    [string]$Action = "status"
)

switch ($Action.ToLower()) {
    "start" {
        Write-Host "Starting Zabbix Stack..." -ForegroundColor Green
        docker compose up -d
        Write-Host "`nZabbix Web UI is available at: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "Default Login -> User: Admin | Password: zabbix" -ForegroundColor Yellow
    }
    "stop" {
        Write-Host "Stopping Zabbix Stack..." -ForegroundColor Red
        docker compose stop
    }
    "down" {
        Write-Host "Tearing down Zabbix Stack..." -ForegroundColor Red
        docker compose down
    }
    "restart" {
        Write-Host "Restarting Zabbix Stack..." -ForegroundColor Yellow
        docker compose restart
    }
    "logs" {
        Write-Host "Showing Zabbix Server Logs..." -ForegroundColor Cyan
        docker logs -f zabbix-server
    }
    "status" {
        Write-Host "=== Zabbix Container Status ===" -ForegroundColor Green
        docker ps --filter "name=zabbix"
        Write-Host "`nZabbix Web URL: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "Default Login -> User: Admin | Password: zabbix" -ForegroundColor Yellow
    }
    default {
        Write-Host "Usage: .\manage-zabbix.ps1 [start|stop|restart|logs|status|down]" -ForegroundColor Yellow
    }
}
