# Simple PowerShell deployment script for WhatsApp Agent to VM

Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "WhatsApp Agent Deployment Script" -ForegroundColor Yellow
Write-Host "Target VM: 129.159.224.220" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""

# Configuration
$VM_IP = "129.159.224.220"
$SSH_KEY_PATH = "C:\Users\kkavi\OneDrive\Desktop\oraclekeys\ssh-key-2025-10-14.key"
$PROJECT_NAME = "whatsapp-agent"
$LOCAL_PROJECT_PATH = "e:\Sunny React Projects\Whatsapp Agent"
$TEMP_TAR_PATH = "$env:TEMP\$PROJECT_NAME.tar.gz"

Write-Host "Step 1: Compressing local project..." -ForegroundColor Yellow

# Check if tar is available (available in Windows 10/11)
if (Get-Command tar -ErrorAction SilentlyContinue) {
    Set-Location $LOCAL_PROJECT_PATH
    & tar -czf $TEMP_TAR_PATH .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Project compressed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to compress project" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ tar command not found. Please install Git Bash or WSL." -ForegroundColor Red
    Write-Host "Alternatively, you can use 7-Zip with the command:" -ForegroundColor Red
    Write-Host "Compress-Archive -Path '$LOCAL_PROJECT_PATH\*' -DestinationPath '$TEMP_TAR_PATH' -Force" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Transferring project to VM..." -ForegroundColor Yellow

# Transfer the compressed project to the VM using scp
$scpCommand = "scp -i `"$SSH_KEY_PATH`" `"$TEMP_TAR_PATH`" ubuntu@$VM_IP`:`"/tmp/`""
$process = Start-Process powershell -ArgumentList "-Command", $scpCommand -PassThru -Wait

if ($process.ExitCode -eq 0) {
    Write-Host "✓ Project transferred successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to transfer project to VM" -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Executing deployment commands on VM..." -ForegroundColor Yellow

# Execute individual commands on the VM
Write-Host "  Updating system packages..." -ForegroundColor Gray
$cmd1 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"sudo apt update && sudo apt upgrade -y`""
Invoke-Expression $cmd1

Write-Host "  Installing Docker..." -ForegroundColor Gray
$cmd2 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo usermod -aG docker \$USER`""
Invoke-Expression $cmd2

Write-Host "  Installing Docker Compose..." -ForegroundColor Gray
$cmd3 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose`""
Invoke-Expression $cmd3

Write-Host "  Installing Git and Nginx..." -ForegroundColor Gray
$cmd4 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"sudo apt install git nginx -y`""
Invoke-Expression $cmd4

Write-Host "  Cleaning up any existing containers..." -ForegroundColor Gray
$cmd5 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"sudo docker system prune -af`""
Invoke-Expression $cmd5

Write-Host "  Creating project directory and extracting..." -ForegroundColor Gray
$cmd6 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"mkdir -p /home/ubuntu/whatsapp-agent && cd /home/ubuntu/whatsapp-agent && tar -xzf /tmp/whatsapp-agent.tar.gz`""
Invoke-Expression $cmd6

Write-Host "  Building and starting services..." -ForegroundColor Gray
$cmd7 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"cd /home/ubuntu/whatsapp-agent && docker-compose -f infra/docker-compose.yml up -d --build`""
Invoke-Expression $cmd7

Start-Sleep -Seconds 60

Write-Host "  Setting up Nginx reverse proxy..." -ForegroundColor Gray
$nginxConfig = @"
server {
    listen 80;
    server_name 129.159.224.220;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ws {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
"@

# Write the nginx config to a temp file and copy it to the VM
$nginxTempPath = "$env:TEMP\whatsapp-agent.conf"
$nginxConfig | Out-File -FilePath $nginxTempPath -Encoding ASCII
$scpNginx = "scp -i `"$SSH_KEY_PATH`" `"$nginxTempPath`" ubuntu@$VM_IP`:`"/tmp/whatsapp-agent.conf`""
Start-Process powershell -ArgumentList "-Command", $scpNginx -PassThru -Wait

# Move the config to nginx sites-available and enable it
$cmd8 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"sudo cp /tmp/whatsapp-agent.conf /etc/nginx/sites-available/whatsapp-agent && sudo ln -sf /etc/nginx/sites-available/whatsapp-agent /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl restart nginx`""
Invoke-Expression $cmd8

Write-Host "  Checking service status..." -ForegroundColor Gray
$cmd9 = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"cd /home/ubuntu/whatsapp-agent && docker-compose -f infra/docker-compose.yml ps`""
$servicesStatus = Invoke-Expression $cmd9

Write-Host "✓ Deployment completed successfully" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "WhatsApp Agent is now deployed on your VM" -ForegroundColor Green
Write-Host "Services Status:" -ForegroundColor Cyan
$servicesStatus
Write-Host ""
Write-Host "Access the API at: http://129.159.224.220" -ForegroundColor Green
Write-Host "API Documentation: http://129.159.224.220/docs" -ForegroundColor Green
Write-Host "Adminer: http://129.159.224.220:8080" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Verify the services are running by accessing the URLs above" -ForegroundColor White
Write-Host "2. Test the API endpoints to ensure functionality" -ForegroundColor White
Write-Host "3. Configure SSL certificate for HTTPS (optional but recommended)" -ForegroundColor White
Write-Host "4. Set up proper domain name if you have one" -ForegroundColor White
Write-Host "5. Monitor the service logs for any issues" -ForegroundColor White
Write-Host ""
Write-Host "To check logs: ssh -i '$SSH_KEY_PATH' ubuntu`@129.159.224.220" -ForegroundColor White
Write-Host "Then run: cd /home/ubuntu/whatsapp-agent; docker-compose -f infra/docker-compose.yml logs" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green