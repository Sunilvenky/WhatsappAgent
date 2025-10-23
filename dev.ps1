# PowerShell equivalent of dev.sh for Windows users
param(
    [string]$Command = "up"
)

if ($Command -eq "up") {
    Write-Host "Starting dev stack with docker-compose..."
    docker-compose -f infra/docker-compose.yml up -d --build
    Write-Host "Waiting for services to become healthy..."
    Start-Sleep 3
    Write-Host "(Stub) Running migrations..."
    # In future: run alembic migrations here
    exit 0
}

if ($Command -eq "down") {
    Write-Host "Stopping dev stack..."
    docker-compose -f infra/docker-compose.yml down
    exit 0
}

Write-Host "Usage: .\dev.ps1 [up|down]"