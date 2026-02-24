# PowerShell deployment script for WhatsApp Agent to VM

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

# Create the deployment script content for the remote VM

# Save the remote script to a temporary file
$tempScriptPath = "$env:TEMP\deploy_script.sh"

# Define the remote script content as an array of lines to avoid parsing issues
$remoteScriptLines = @(
    "set -e",
    "",
    "echo ""Updating system packages...""",
    "sudo apt update && sudo apt upgrade -y",
    "",
    "echo ""Installing Docker...""",
    "curl -fsSL https://get.docker.com -o get-docker.sh",
    "sh get-docker.sh",
    "sudo usermod -aG docker \$USER",
    "",
    "echo ""Installing Docker Compose...""",
    "sudo curl -L ""https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)"" -o /usr/local/bin/docker-compose",
    "sudo chmod +x /usr/local/bin/docker-compose",
    "",
    "echo ""Installing Git and Nginx...""",
    "sudo apt install git nginx -y",
    "",
    "echo ""Cleaning up any existing containers...""",
    "sudo docker system prune -af",
    "",
    "echo ""Creating project directory...""",
    "mkdir -p /home/ubuntu/whatsapp-agent",
    "cd /home/ubuntu/whatsapp-agent",
    "",
    "echo ""Extracting project files...""",
    "tar -xzf /tmp/whatsapp-agent.tar.gz",
    "",
    "echo ""Building and starting services...""",
    "docker-compose -f infra/docker-compose.yml up -d --build",
    "",
    "echo ""Waiting for services to start...""",
    "sleep 60",
    "",
    "echo ""Checking service status...""",
    "docker-compose -f infra/docker-compose.yml ps",
    "",
    "echo ""Setting up Nginx reverse proxy...""",
    "sudo tee /etc/nginx/sites-available/whatsapp-agent > /dev/null <<NGINX_EOF",
    "server {",
    "    listen 80;",
    "    server_name 129.159.224.220;",
    "",
    "    location / {",
    "        proxy_pass http://localhost:3000;",
    "        proxy_set_header Host \$host;",
    "        proxy_set_header X-Real-IP \$remote_addr;",
    "        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;",
    "        proxy_set_header X-Forwarded-Proto \$scheme;",
    "    }",
    "",
    "    location /api/ {",
    "        proxy_pass http://localhost:3000;",
    "        proxy_set_header Host \$host;",
    "        proxy_set_header X-Real-IP \$remote_addr;",
    "        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;",
    "        proxy_set_header X-Forwarded-Proto \$scheme;",
    "    }",
    "",
    "    location /ws {",
    "        proxy_pass http://localhost:3000;",
    "        proxy_http_version 1.1;",
    "        proxy_set_header Upgrade \$http_upgrade;",
    "        proxy_set_header Connection ""upgrade"";",
    "        proxy_set_header Host \$host;",
    "        proxy_set_header X-Real-IP \$remote_addr;",
    "        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;",
    "        proxy_set_header X-Forwarded-Proto \$scheme;",
    "    }",
    "}",
    "NGINX_EOF",
    "",
    "sudo ln -s /etc/nginx/sites-available/whatsapp-agent /etc/nginx/sites-enabled/",
    "sudo nginx -t",
    "sudo systemctl restart nginx",
    "",
    "echo ""Deployment completed successfully!""",
    "echo ""Services status:""",
    "docker-compose -f infra/docker-compose.yml ps",
    "",
    "# Output final status",
    "echo """";",
    "echo ""=========================================="";",
    "echo ""DEPLOYMENT SUCCESSFUL!"";",
    "echo ""=========================================="";",
    "echo ""WhatsApp Agent is now deployed on your VM"";",
    "echo ""Access the API at: http://129.159.224.220"";",
    "echo ""API Documentation: http://129.159.224.220/docs"";",
    "echo ""Adminer: http://129.159.224.220:8080"";",
    "echo """";",
    "echo ""NEXT STEPS:"";",
    "echo ""1. Verify the services are running by accessing the URLs above"";",
    "echo ""2. Test the API endpoints to ensure functionality"";",
    "echo ""3. Configure SSL certificate for HTTPS (optional but recommended)"";",
    "echo ""4. Set up proper domain name if you have one"";",
    "echo ""5. Monitor the service logs for any issues"";",
    "echo """";",
    "echo ""To check logs: ssh -i 'C:\\Users\\kkavi\\OneDrive\\Desktop\\oraclekeys\\ssh-key-2025-10-14.key' ubuntu`@129.159.224.220"";",
    "echo ""Then run: cd /home/ubuntu/whatsapp-agent; docker-compose -f infra/docker-compose.yml logs"";",
    "echo ""=========================================="";"
)

$remoteScript = $remoteScriptLines -join "`n"

# Save the remote script to a temporary file
$remoteScript | Out-File -FilePath $tempScriptPath -Encoding UTF8

# Transfer the script to the VM
$scpScriptCommand = "scp -i `"$SSH_KEY_PATH`" `"$tempScriptPath`" ubuntu@$VM_IP`:/tmp/deploy_script.sh"
Start-Process powershell -ArgumentList "-Command", $scpScriptCommand -PassThru -Wait

# Execute the script on the VM
$sshCommand = "ssh -i `"$SSH_KEY_PATH`" ubuntu@$VM_IP `"bash /tmp/deploy_script.sh`""
$sshResult = $(Invoke-Expression $sshCommand 2>&1)
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Output "✓ Deployment completed successfully"
    Write-Output ""
    Write-Output "=========================================="
    Write-Output "DEPLOYMENT SUCCESSFUL!"
    Write-Output "=========================================="
    Write-Output "WhatsApp Agent is now deployed on your VM"
    Write-Output "Access the API at: http://129.159.224.220"
    Write-Output "API Documentation: http://129.159.224.220/docs"
    Write-Output "Adminer: http://129.159.224.220:8080"
    Write-Output ""
    Write-Output "NEXT STEPS:"
    Write-Output "1. Verify the services are running by accessing the URLs above"
    Write-Output "2. Test the API endpoints to ensure functionality"
    Write-Output "3. Configure SSL certificate for HTTPS (optional but recommended)"
    Write-Output "4. Set up proper domain name if you have one"
    Write-Output "5. Monitor the service logs for any issues"
    Write-Output ""
    Write-Output "To check logs: ssh -i '$SSH_KEY_PATH' ubuntu`@129.159.224.220"
    Write-Output "Then run: cd /home/ubuntu/whatsapp-agent; docker-compose -f infra/docker-compose.yml logs"
    Write-Output "=========================================="
} else {
    Write-Output "✗ Deployment failed"
    Write-Output "SSH Command completed with exit code: " $exitCode
    exit 1
}