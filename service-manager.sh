#!/bin/bash
# AD Portal Service Manager
# Quick access to common service operations

SERVICE_NAME="ad-portal"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_usage() {
    echo -e "${BLUE}AD Portal Service Manager${NC}\n"
    echo "Usage: ./service-manager.sh [command]"
    echo ""
    echo "Commands:"
    echo "  status    - Show service status"
    echo "  start     - Start the service"
    echo "  stop      - Stop the service"
    echo "  restart   - Restart the service"
    echo "  logs      - Show live logs (Ctrl+C to exit)"
    echo "  enable    - Enable service to start on boot"
    echo "  disable   - Disable service from starting on boot"
    echo "  tail      - Show last 50 log lines"
    echo ""
}

check_sudo() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}❌ This command requires sudo${NC}"
        echo -e "${YELLOW}Run: sudo ./service-manager.sh $1${NC}"
        exit 1
    fi
}

case "$1" in
    status)
        echo -e "${BLUE}Checking service status...${NC}\n"
        sudo systemctl status $SERVICE_NAME.service --no-pager
        ;;
    start)
        check_sudo "start"
        echo -e "${YELLOW}Starting service...${NC}"
        systemctl start $SERVICE_NAME.service
        sleep 2
        if systemctl is-active --quiet $SERVICE_NAME.service; then
            echo -e "${GREEN}✅ Service started successfully${NC}"
            echo -e "${BLUE}Access at: http://localhost:8501${NC}"
        else
            echo -e "${RED}❌ Failed to start service${NC}"
            exit 1
        fi
        ;;
    stop)
        check_sudo "stop"
        echo -e "${YELLOW}Stopping service...${NC}"
        systemctl stop $SERVICE_NAME.service
        echo -e "${GREEN}✅ Service stopped${NC}"
        ;;
    restart)
        check_sudo "restart"
        echo -e "${YELLOW}Restarting service...${NC}"
        systemctl restart $SERVICE_NAME.service
        sleep 2
        if systemctl is-active --quiet $SERVICE_NAME.service; then
            echo -e "${GREEN}✅ Service restarted successfully${NC}"
            echo -e "${BLUE}Access at: http://localhost:8501${NC}"
        else
            echo -e "${RED}❌ Failed to restart service${NC}"
            exit 1
        fi
        ;;
    logs)
        echo -e "${BLUE}Showing live logs (Ctrl+C to exit)...${NC}\n"
        sudo journalctl -u $SERVICE_NAME.service -f
        ;;
    tail)
        echo -e "${BLUE}Last 50 log entries:${NC}\n"
        sudo journalctl -u $SERVICE_NAME.service -n 50 --no-pager
        ;;
    enable)
        check_sudo "enable"
        echo -e "${YELLOW}Enabling service for automatic startup...${NC}"
        systemctl enable $SERVICE_NAME.service
        echo -e "${GREEN}✅ Service will start automatically on boot${NC}"
        ;;
    disable)
        check_sudo "disable"
        echo -e "${YELLOW}Disabling service from automatic startup...${NC}"
        systemctl disable $SERVICE_NAME.service
        echo -e "${GREEN}✅ Service will not start automatically on boot${NC}"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
