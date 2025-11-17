#!/bin/bash
# Active Directory Portal - Service Uninstall Script
# This script removes the AD Portal systemd service

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - Should match your deployment settings
# ============================================================================
SERVICE_NAME="ad-portal"
SYSTEMD_PATH="/etc/systemd/system"
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AD Portal Service Uninstall${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Error: This script must be run with sudo${NC}"
    echo -e "${YELLOW}Usage: sudo bash uninstall-service.sh${NC}\n"
    exit 1
fi

# Step 1: Stop the service
echo -e "${YELLOW}Step 1: Stopping the service...${NC}"
systemctl stop $SERVICE_NAME.service 2>/dev/null || true
echo -e "${GREEN}✅ Service stopped${NC}\n"

# Step 2: Disable the service
echo -e "${YELLOW}Step 2: Disabling the service...${NC}"
systemctl disable $SERVICE_NAME.service 2>/dev/null || true
echo -e "${GREEN}✅ Service disabled${NC}\n"

# Step 3: Remove service file
echo -e "${YELLOW}Step 3: Removing service file...${NC}"
rm -f "$SYSTEMD_PATH/$SERVICE_NAME.service"
echo -e "${GREEN}✅ Service file removed${NC}\n"

# Step 4: Reload systemd daemon
echo -e "${YELLOW}Step 4: Reloading systemd daemon...${NC}"
systemctl daemon-reload
systemctl reset-failed 2>/dev/null || true
echo -e "${GREEN}✅ Systemd daemon reloaded${NC}\n"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Uninstall Complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}💡 Note: You can still run the application manually:${NC}"
echo -e "   ${BLUE}cd ~/_wf/active-directory${NC}"
echo -e "   ${BLUE}streamlit run streamlit_ad_portal_app.py${NC}\n"
