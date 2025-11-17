# 🚀 Service Deployment Guide

## Quick Start (Recommended Method)

### Option 1: Automatic Deployment (One Command)

```bash
cd /path/to/active-directory
sudo bash deploy-service.sh
```

The script will automatically detect:
- Current directory path
- Your username
- Streamlit installation path
- And generate the service file with correct paths

This will:
- ✅ Stop existing processes
- ✅ Install systemd service
- ✅ Enable auto-start on boot
- ✅ Start the service
- ✅ Verify deployment

---

## Manual Deployment (Step-by-Step)

If you prefer manual control or the automatic script fails:

### Step 1: Stop Existing Processes
```bash
pkill -f "streamlit run"
```

### Step 2: Copy Service File
```bash
sudo cp ad-portal.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/ad-portal.service
```

### Step 3: Reload Systemd
```bash
sudo systemctl daemon-reload
```

### Step 4: Enable Service (Start on Boot)
```bash
sudo systemctl enable ad-portal.service
```

### Step 5: Start Service
```bash
sudo systemctl start ad-portal.service
```

### Step 6: Verify Status
```bash
sudo systemctl status ad-portal.service
```

---

## Service Management

### Using Service Manager Script (Easy Way)

```bash
# Check status
./service-manager.sh status

# Start service
sudo ./service-manager.sh start

# Stop service
sudo ./service-manager.sh stop

# Restart service
sudo ./service-manager.sh restart

# View live logs
sudo ./service-manager.sh logs

# View last 50 log entries
./service-manager.sh tail

# Enable auto-start on boot
sudo ./service-manager.sh enable

# Disable auto-start on boot
sudo ./service-manager.sh disable
```

### Using Systemctl Directly

```bash
# Check service status
sudo systemctl status ad-portal.service

# Start service
sudo systemctl start ad-portal.service

# Stop service
sudo systemctl stop ad-portal.service

# Restart service
sudo systemctl restart ad-portal.service

# Enable auto-start on boot
sudo systemctl enable ad-portal.service

# Disable auto-start
sudo systemctl disable ad-portal.service

# View logs (live)
sudo journalctl -u ad-portal.service -f

# View last 100 log entries
sudo journalctl -u ad-portal.service -n 100

# View logs since today
sudo journalctl -u ad-portal.service --since today

# View logs for specific time range
sudo journalctl -u ad-portal.service --since "2025-10-16 10:00:00" --until "2025-10-16 12:00:00"
```

---

## Access URLs

After deployment, access the application at:

- **Local**: http://localhost:8501
- **Network**: http://YOUR_SERVER_IP:8501

To find your server IP:
```bash
hostname -I | awk '{print $1}'
```

---

## Files Created

### Service Files
- `ad-portal.service` - Systemd service configuration
- `deploy-service.sh` - Automatic deployment script
- `uninstall-service.sh` - Service removal script
- `service-manager.sh` - Service management helper

### Log Files
- `~/_wf/active-directory/streamlit.log` - Application logs
- `journalctl -u ad-portal.service` - System service logs

---

## Service Configuration Details

The service is configured with:

| Setting | Value | Description |
|---------|-------|-------------|
| User | xyz | Service runs as user 'xyz' |
| Working Directory | ~/_wf/active-directory | Application directory |
| Port | 8501 | Web interface port |
| Auto-restart | Yes | Restarts automatically if crashed |
| Restart Delay | 10 seconds | Wait before restart |
| Memory Limit | 512MB | Maximum memory usage |
| Start on Boot | Yes (if enabled) | Starts automatically |

---

## Troubleshooting

### Service Won't Start

**Check status and logs:**
```bash
sudo systemctl status ad-portal.service
sudo journalctl -u ad-portal.service -n 50
```

**Common issues:**

1. **Port already in use**
   ```bash
   # Check what's using port 8501
   sudo lsof -i :8501
   
   # Kill the process
   sudo kill -9 <PID>
   
   # Restart service
   sudo systemctl restart ad-portal.service
   ```

2. **Permission errors**
   ```bash
   # Fix file permissions
   chmod 644 /etc/systemd/system/ad-portal.service
   sudo systemctl daemon-reload
   ```

3. **Python/Streamlit not found**
   ```bash
   # Verify paths in service file
   which streamlit
   which python3
   
   # Update ad-portal.service if needed
   sudo nano /etc/systemd/system/ad-portal.service
   sudo systemctl daemon-reload
   sudo systemctl restart ad-portal.service
   ```

### Service Crashes Repeatedly

**View crash logs:**
```bash
sudo journalctl -u ad-portal.service -n 100 --no-pager
```

**Check application logs:**
```bash
tail -100 ~/_wf/active-directory/streamlit.log
```

**Test manually:**
```bash
# Stop service
sudo systemctl stop ad-portal.service

# Run manually to see errors
cd ~/_wf/active-directory
streamlit run streamlit_ad_portal_app.py
```

### Can't Access from Network

**Check firewall:**
```bash
# Allow port 8501
sudo ufw allow 8501/tcp
sudo ufw reload
```

**Verify service is listening on all interfaces:**
```bash
sudo netstat -tulpn | grep 8501
# Should show 0.0.0.0:8501
```

---

## Uninstalling the Service

### Option 1: Automatic Uninstall
```bash
sudo bash uninstall-service.sh
```

### Option 2: Manual Uninstall
```bash
# Stop service
sudo systemctl stop ad-portal.service

# Disable service
sudo systemctl disable ad-portal.service

# Remove service file
sudo rm /etc/systemd/system/ad-portal.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

After uninstall, you can still run manually:
```bash
cd ~/_wf/active-directory
streamlit run streamlit_ad_portal_app.py
```

---

## Updating the Application

When you update the code:

```bash
# Option 1: Restart service (recommended)
sudo systemctl restart ad-portal.service

# Option 2: Full reload
sudo systemctl stop ad-portal.service
sudo systemctl start ad-portal.service

# Option 3: Using service manager
sudo ./service-manager.sh restart
```

---

## Backup and Restore

### Backup
```bash
# Backup data
cp employees.xlsx employees-backup-$(date +%Y%m%d).xlsx

# Backup service file
sudo cp /etc/systemd/system/ad-portal.service ad-portal.service.backup
```

### Restore
```bash
# Restore data
cp employees-backup-YYYYMMDD.xlsx employees.xlsx

# Restart service to load new data
sudo systemctl restart ad-portal.service
```

---

## Performance Monitoring

### Check CPU and Memory Usage
```bash
# View process info
ps aux | grep streamlit

# View detailed stats
sudo systemctl status ad-portal.service
```

### View Resource Limits
```bash
sudo systemctl show ad-portal.service | grep -E "Memory|CPUQuota|TasksMax"
```

### Adjust Memory Limit
```bash
# Edit service file
sudo nano /etc/systemd/system/ad-portal.service

# Change: MemoryLimit=512M to desired value (e.g., 1G)

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ad-portal.service
```

---

## Security Best Practices

1. **Firewall Configuration**
   ```bash
   # Only allow specific IPs (replace X.X.X.X with your IP)
   sudo ufw allow from X.X.X.X to any port 8501
   ```

2. **HTTPS Setup** (Recommended for production)
   - Use Nginx as reverse proxy with SSL
   - See main DEPLOYMENT_GUIDE.md for details

3. **File Permissions**
   ```bash
   # Secure the Excel file
   chmod 600 employees.xlsx
   
   # Secure log files
   chmod 640 streamlit.log
   ```

4. **Regular Backups**
   ```bash
   # Add to crontab for daily backups
   crontab -e
   
   # Add this line:
   0 2 * * * cp ~/_wf/active-directory/employees.xlsx ~/_wf/active-directory/backups/employees-$(date +\%Y\%m\%d).xlsx
   ```

---

## Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Viewer Account:**
- Username: `viewer`
- Password: `viewer123`

⚠️ **IMPORTANT**: Change these passwords after deployment!

Edit the Users sheet in `employees.xlsx` and restart the service.

---

## Quick Reference Card

```bash
# Install service
sudo bash deploy-service.sh

# Check status
sudo systemctl status ad-portal.service

# View logs
sudo journalctl -u ad-portal.service -f

# Restart
sudo systemctl restart ad-portal.service

# Uninstall
sudo bash uninstall-service.sh

# Access URL
http://localhost:8501
```

---

## Support

**Logs Location:**
- Application: `~/_wf/active-directory/streamlit.log`
- Service: `sudo journalctl -u ad-portal.service`

**Common Commands:**
```bash
# Full diagnostic
sudo systemctl status ad-portal.service
sudo journalctl -u ad-portal.service -n 50
tail -50 ~/_wf/active-directory/streamlit.log
ps aux | grep streamlit
sudo netstat -tulpn | grep 8501
```

---

**Version**: 1.0  
**Last Updated**: October 16, 2025  
**Service Name**: ad-portal.service  
**Status**: Production Ready ✅
