@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo WhatsApp Agent Deployment Script
echo Target VM: 129.159.227.138
echo ==========================================
echo.

REM Configuration
set VM_IP=129.159.227.138
set SSH_KEY_PATH=C:\Users\kkavi\OneDrive\Desktop\oraclekeys\ssh-key-2025-10-14.key
set PROJECT_NAME=whatsapp-agent
set LOCAL_PROJECT_PATH=e:\Sunny React Projects\Whatsapp Agent
set TEMP_TAR_PATH=%TEMP%\%PROJECT_NAME%.tar.gz

echo Step 1: Compressing local project...
echo.

REM Change to project directory and compress
cd /d "%LOCAL_PROJECT_PATH%"
tar -czf "%TEMP_TAR_PATH%" .

if %errorlevel% neq 0 (
    echo Error: Failed to compress project
    exit /b 1
)

echo ^<^<^< Project compressed successfully ^>^>^>

echo.
echo Step 2: Transferring project to VM...
echo.

REM Transfer the compressed project to the VM using scp
scp -i "%SSH_KEY_PATH%" "%TEMP_TAR_PATH%" ubuntu@%VM_IP%:/tmp/

if %errorlevel% neq 0 (
    echo Error: Failed to transfer project to VM
    exit /b 1
)

echo ^<^<^< Project transferred successfully ^>^>^>

echo.
echo Step 3: Executing deployment commands on VM...
echo.

echo   Updating system packages...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "sudo apt update && sudo apt upgrade -y"

echo   Installing Docker...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo usermod -aG docker $USER"

echo   Installing Docker Compose...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"

echo   Installing Git and Nginx...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "sudo apt install git nginx -y"

echo   Cleaning up any existing containers...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "sudo docker system prune -af"

echo   Creating project directory and extracting...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "mkdir -p /home/ubuntu/whatsapp-agent && cd /home/ubuntu/whatsapp-agent && tar -xzf /tmp/whatsapp-agent.tar.gz"

echo   Building and starting services...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "cd /home/ubuntu/whatsapp-agent && docker-compose -f infra/docker-compose.yml up -d --build"

REM Wait for services to start
echo   Waiting for services to start...
timeout /t 60 /nobreak >nul

REM Create nginx configuration locally and transfer it
echo server ^{ > %TEMP%\whatsapp-agent.conf
echo     listen 80^; >> %TEMP%\whatsapp-agent.conf
echo     server_name 129.159.227.138^; >> %TEMP%\whatsapp-agent.conf
echo. >> %TEMP%\whatsapp-agent.conf
echo     location / ^{ >> %TEMP%\whatsapp-agent.conf
echo         proxy_pass http://localhost:3000^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header Host $host^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Real-IP $remote_addr^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-Proto $scheme^; >> %TEMP%\whatsapp-agent.conf
echo     ^} >> %TEMP%\whatsapp-agent.conf
echo. >> %TEMP%\whatsapp-agent.conf
echo     location /api/ ^{ >> %TEMP%\whatsapp-agent.conf
echo         proxy_pass http://localhost:3000^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header Host $host^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Real-IP $remote_addr^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-Proto $scheme^; >> %TEMP%\whatsapp-agent.conf
echo     ^} >> %TEMP%\whatsapp-agent.conf
echo. >> %TEMP%\whatsapp-agent.conf
echo     location /ws ^{ >> %TEMP%\whatsapp-agent.conf
echo         proxy_pass http://localhost:3000^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_http_version 1.1^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header Upgrade $http_upgrade^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header Connection "upgrade"^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header Host $host^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Real-IP $remote_addr^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for^; >> %TEMP%\whatsapp-agent.conf
echo         proxy_set_header X-Forwarded-Proto $scheme^; >> %TEMP%\whatsapp-agent.conf
echo     ^} >> %TEMP%\whatsapp-agent.conf
echo ^} >> %TEMP%\whatsapp-agent.conf

echo   Transferring Nginx configuration...
scp -i "%SSH_KEY_PATH%" %TEMP%\whatsapp-agent.conf ubuntu@%VM_IP%:/tmp/whatsapp-agent.conf

echo   Setting up Nginx reverse proxy...
ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "sudo cp /tmp/whatsapp-agent.conf /etc/nginx/sites-available/whatsapp-agent && sudo ln -sf /etc/nginx/sites-available/whatsapp-agent /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl restart nginx"

echo   Checking service status...
for /f %%i in ('ssh -i "%SSH_KEY_PATH%" ubuntu@%VM_IP% "cd /home/ubuntu/whatsapp-agent && docker-compose -f infra/docker-compose.yml ps --format json"') do set SERVICES_STATUS=%%i

echo.
echo ^<^<^< Deployment completed successfully ^>^>^>
echo.
echo =========================================
echo DEPLOYMENT SUCCESSFUL!
echo =========================================
echo WhatsApp Agent is now deployed on your VM
echo Services Status: !SERVICES_STATUS!
echo.
echo Access the API at: http://129.159.227.138
echo API Documentation: http://129.159.227.138/docs
echo Adminer: http://129.159.227.138:8080
echo.
echo NEXT STEPS:
echo 1. Verify the services are running by accessing the URLs above
echo 2. Test the API endpoints to ensure functionality
echo 3. Configure SSL certificate for HTTPS (optional but recommended)
echo 4. Set up proper domain name if you have one
echo 5. Monitor the service logs for any issues
echo.
echo To check logs: ssh -i '%SSH_KEY_PATH%' ubuntu@%VM_IP%
echo Then run: cd /home/ubuntu/whatsapp-agent ^&^& docker-compose -f infra/docker-compose.yml logs
echo =========================================

endlocal