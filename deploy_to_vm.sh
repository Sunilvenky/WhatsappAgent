#!/bin/bash
# Deployment script for WhatsApp Agent to VM

echo "=========================================="
echo "WhatsApp Agent Deployment Script"
echo "Target VM: 129.159.227.138"
echo "=========================================="
echo ""

# Configuration
VM_IP="129.159.227.138"
SSH_KEY_PATH="C:\Users\kkavi\OneDrive\Desktop\oraclekeys\ssh-key-2025-10-14.key"
PROJECT_NAME="whatsapp-agent"
REMOTE_PROJECT_PATH="/home/ubuntu/whatsapp-agent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Compressing local project...${NC}"

# Compress the project locally
cd "e:/Sunny React Projects/Whatsapp Agent" || { echo "Error: Cannot access project directory"; exit 1; }
tar -czf "../${PROJECT_NAME}.tar.gz" .

echo -e "${GREEN}✓ Project compressed successfully${NC}"

echo -e "${YELLOW}Step 2: Transferring project to VM...${NC}"

# Transfer the compressed project to the VM
scp -i "$SSH_KEY_PATH" "../$PROJECT_NAME.tar.gz" ubuntu@$VM_IP:/tmp/

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to transfer project to VM${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project transferred successfully${NC}"

echo -e "${YELLOW}Step 3: Executing deployment commands on VM...${NC}"

# Execute the deployment commands on the VM
ssh -i "$SSH_KEY_PATH" ubuntu@$VM_IP << 'EOF'
set -e

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Installing Git and Nginx..."
sudo apt install git nginx -y

echo "Cleaning up any existing containers..."
sudo docker system prune -af

echo "Creating project directory..."
mkdir -p /home/ubuntu/whatsapp-agent
cd /home/ubuntu/whatsapp-agent

echo "Extracting project files..."
tar -xzf /tmp/whatsapp-agent.tar.gz

echo "Building and starting services..."
docker-compose -f infra/docker-compose.yml up -d --build

echo "Waiting for services to start..."
sleep 60

echo "Checking service status..."
docker-compose -f infra/docker-compose.yml ps

echo "Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/whatsapp-agent > /dev/null <<NGINX_EOF
server {
    listen 80;
    server_name 129.159.227.138;

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
NGINX_EOF

sudo ln -s /etc/nginx/sites-available/whatsapp-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "Deployment completed successfully!"
echo "Services status:"
docker-compose -f infra/docker-compose.yml ps

EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment completed successfully${NC}"
    echo ""
    echo "=========================================="
    echo "DEPLOYMENT SUCCESSFUL!"
    echo "=========================================="
    echo "WhatsApp Agent is now deployed on your VM"
    echo "Access the API at: http://129.159.227.138"
    echo "API Documentation: http://129.159.227.138/docs"
    echo "Adminer: http://129.159.227.138:8080"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Verify the services are running by accessing the URLs above"
    echo "2. Test the API endpoints to ensure functionality"
    echo "3. Configure SSL certificate for HTTPS (optional but recommended)"
    echo "4. Set up proper domain name if you have one"
    echo "5. Monitor the service logs for any issues"
    echo ""
    echo "To check logs: ssh -i '$SSH_KEY_PATH' ubuntu@$VM_IP"
    echo "Then run: cd /home/ubuntu/whatsapp-agent && docker-compose -f infra/docker-compose.yml logs"
    echo "=========================================="
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi