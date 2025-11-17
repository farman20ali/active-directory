#!/bin/bash
# Active Directory Portal - Service Deployment Script
# This script installs and configures the AD Portal as a systemd service

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - Edit these variables before deployment
# ============================================================================
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # Auto-detect current directory
APP_USER="${SUDO_USER:-${USER}}"  # Detect real user even when run with sudo
STREAMLIT_PATH="/home/${APP_USER}/.local/bin/streamlit"  # Streamlit path
SERVICE_NAME="ad-portal"
SERVICE_FILE="ad-portal.service"
SYSTEMD_PATH="/etc/systemd/system"
LOG_FILE="$APP_DIR/streamlit.log"
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AD Portal Service Deployment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Display detected configuration
echo -e "${BLUE}📋 Detected Configuration:${NC}"
echo -e "   App Directory: ${GREEN}$APP_DIR${NC}"
echo -e "   App User:      ${GREEN}$APP_USER${NC}"
echo -e "   Streamlit:     ${GREEN}$STREAMLIT_PATH${NC}"
echo -e "   Service Name:  ${GREEN}$SERVICE_NAME${NC}\n"

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Error: This script must be run with sudo${NC}"
    echo -e "${YELLOW}Usage: sudo bash deploy-service.sh${NC}\n"
    exit 1
fi

# Verify streamlit is installed
if [ -z "$STREAMLIT_PATH" ]; then
    echo -e "${RED}❌ Error: Streamlit not found in PATH${NC}"
    echo -e "${YELLOW}Install with: pip install streamlit${NC}\n"
    exit 1
fi

# Step 1: Stop any existing Streamlit processes
echo -e "${YELLOW}Step 1: Stopping existing Streamlit processes...${NC}"
pkill -f "streamlit run" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Existing processes stopped${NC}\n"

# Step 2: Generate service file with correct paths
echo -e "${YELLOW}Step 2: Generating service file...${NC}"

# Create service file with actual paths
cat > "$APP_DIR/$SERVICE_FILE" << EOF
[Unit]
Description=Active Directory Portal - Streamlit Application
After=network.target
Documentation=https://github.com/streamlit/streamlit

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$(dirname $STREAMLIT_PATH):/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$STREAMLIT_PATH run streamlit_ad_portal_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

# Security settings
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=4096
MemoryLimit=512M

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service file generated${NC}\n"

# Step 3: Copy service file to systemd directory
echo -e "${YELLOW}Step 3: Installing service file...${NC}"
cp "$APP_DIR/$SERVICE_FILE" "$SYSTEMD_PATH/$SERVICE_NAME.service"
chmod 644 "$SYSTEMD_PATH/$SERVICE_NAME.service"
echo -e "${GREEN}✅ Service file installed to $SYSTEMD_PATH${NC}\n"

# Step 4: Reload systemd daemon
echo -e "${YELLOW}Step 4: Reloading systemd daemon...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd daemon reloaded${NC}\n"

# Step 5: Enable service to start on boot
echo -e "${YELLOW}Step 5: Enabling service to start on boot...${NC}"
systemctl enable $SERVICE_NAME.service
echo -e "${GREEN}✅ Service enabled for automatic startup${NC}\n"

# Step 6: Start the service
echo -e "${YELLOW}Step 6: Starting the service...${NC}"
systemctl start $SERVICE_NAME.service
sleep 3
echo -e "${GREEN}✅ Service started${NC}\n"

# Step 7: Check service status
echo -e "${YELLOW}Step 7: Checking service status...${NC}"
if systemctl is-active --quiet $SERVICE_NAME.service; then
    echo -e "${GREEN}✅ Service is running successfully!${NC}\n"
    
    # Show service status
    echo -e "${BLUE}Service Status:${NC}"
    systemctl status $SERVICE_NAME.service --no-pager | head -20
    
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 Deployment Successful!${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    echo -e "${GREEN}📍 Access URLs:${NC}"
    echo -e "   Local:    ${BLUE}http://localhost:8501${NC}"
    echo -e "   Network:  ${BLUE}http://$(hostname -I | awk '{print $1}'):8501${NC}\n"
    
    echo -e "${GREEN}📋 Useful Commands:${NC}"
    echo -e "   Check status:  ${BLUE}sudo systemctl status $SERVICE_NAME${NC}"
    echo -e "   Stop service:  ${BLUE}sudo systemctl stop $SERVICE_NAME${NC}"
    echo -e "   Start service: ${BLUE}sudo systemctl start $SERVICE_NAME${NC}"
    echo -e "   Restart:       ${BLUE}sudo systemctl restart $SERVICE_NAME${NC}"
    echo -e "   View logs:     ${BLUE}sudo journalctl -u $SERVICE_NAME -f${NC}"
    echo -e "   Disable:       ${BLUE}sudo systemctl disable $SERVICE_NAME${NC}\n"
    
    echo -e "${GREEN}📝 Log File:${NC}"
    echo -e "   ${BLUE}$LOG_FILE${NC}\n"
    
    echo -e "${YELLOW}💡 Tip: The service will automatically start on system boot!${NC}\n"
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo -e "${YELLOW}Checking logs...${NC}\n"
    journalctl -u $SERVICE_NAME.service -n 50 --no-pager
    exit 1
fi
