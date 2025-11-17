# 📋 Active Directory Portal - Configuration Guide

## For New Installations

This guide will help you configure the application for your environment.

---

## 🔧 Configuration Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd active-directory
```

### 2. Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Paths (For Service Deployment)

The deployment script **automatically detects**:
- Your username
- Installation directory
- Streamlit path

No manual configuration needed! Just run:

```bash
sudo bash deploy-service.sh
```

The script will:
- ✅ Auto-detect your paths
- ✅ Generate service file with correct settings
- ✅ Install and start the service

---

## 📝 Manual Configuration (Optional)

If you need custom paths, edit these variables in `deploy-service.sh`:

```bash
# Open the script
nano deploy-service.sh

# Edit the CONFIGURATION section:
APP_DIR="/your/custom/path"        # Application directory
APP_USER="your_username"           # Your username
STREAMLIT_PATH="/path/to/streamlit" # Streamlit binary path
```

---

## 🗂️ File Structure

```
active-directory/
├── streamlit_ad_portal_app.py    # Main application
├── requirements.txt               # Python dependencies
├── employees-sample.xlsx          # Sample data file
├── sample_bulk_upload.csv         # Sample bulk upload
├── deploy-service.sh              # Auto-deployment script
├── uninstall-service.sh           # Service removal script
├── service-manager.sh             # Service management helper
├── ad-portal.service.template     # Service template
├── .gitignore                     # Git ignore rules
├── README.md                      # Main documentation
├── SERVICE_DEPLOYMENT.md          # Deployment guide
└── CONFIGURATION.md               # This file
```

---

## 🚀 Deployment Options

### Option 1: Systemd Service (Recommended)

**Auto-start on boot, auto-restart on crash**

```bash
sudo bash deploy-service.sh
```

### Option 2: Manual Run

**For testing or development**

```bash
streamlit run streamlit_ad_portal_app.py
```

### Option 3: Background Process

**Simple background execution**

```bash
nohup streamlit run streamlit_ad_portal_app.py > streamlit.log 2>&1 &
```

---

## 🔐 Default Credentials

After first run, login with:

| Role   | Username | Password  |
|--------|----------|-----------|
| Admin  | admin    | admin123  |
| Viewer | viewer   | viewer123 |

⚠️ **IMPORTANT**: Change these passwords immediately!

Edit the `Users` sheet in `employees.xlsx` and restart the service.

---

## 📊 Data Files

### Sample Files (Included in Repo)
- `employees-sample.xlsx` - Sample employee data
- `sample_bulk_upload.csv` - Sample CSV for bulk import

### Generated Files (Not in Repo)
- `employees.xlsx` - Your actual data (auto-created)
- `employees-backup*.xlsx` - Backup files
- `streamlit.log` - Application logs

---

## 🔒 Security Recommendations

### 1. Change Default Passwords
```bash
# Edit the Excel file
libreoffice employees.xlsx  # Or use Excel

# Navigate to Users sheet
# Update passwords for admin and viewer

# Restart service
sudo systemctl restart ad-portal
```

### 2. Set File Permissions
```bash
chmod 600 employees.xlsx         # Owner read/write only
chmod 640 streamlit.log          # Owner read/write, group read
```

### 3. Enable Firewall
```bash
sudo ufw allow from YOUR_IP to any port 8501
sudo ufw enable
```

### 4. Use HTTPS (Production)
See `SERVICE_DEPLOYMENT.md` for Nginx + SSL setup

---

## 🛠️ Troubleshooting

### Service Won't Start

```bash
# Check status
sudo systemctl status ad-portal

# View logs
sudo journalctl -u ad-portal -n 50

# Check if Streamlit is installed
which streamlit
```

### Python Module Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill it
sudo kill -9 <PID>

# Restart service
sudo systemctl restart ad-portal
```

### Cross-Device Link Error

**This has been fixed!** The application now:
- Creates temp files in the same directory as the target
- Uses `shutil.move()` instead of `os.replace()`
- Works across different filesystems

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation and features |
| `SERVICE_DEPLOYMENT.md` | Complete deployment guide |
| `CONFIGURATION.md` | This file - configuration help |
| `QUICK_REFERENCE.txt` | Command cheat sheet |

---

## 🔄 Updating the Application

### If Using Git

```bash
# Pull latest changes
git pull

# Restart service
sudo systemctl restart ad-portal
```

### Manual Update

```bash
# Replace the Python file
cp streamlit_ad_portal_app.py.new streamlit_ad_portal_app.py

# Restart service
sudo systemctl restart ad-portal
```

---

## 🌐 Network Access

### Local Only (Default)
```
http://localhost:8501
```

### Network Access
```
http://YOUR_SERVER_IP:8501
```

Find your IP:
```bash
hostname -I | awk '{print $1}'
```

---

## 💾 Backup Strategy

### Manual Backup
```bash
# Backup data
cp employees.xlsx backups/employees-$(date +%Y%m%d).xlsx
```

### Automated Backup (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cp /path/to/active-directory/employees.xlsx /path/to/backups/employees-$(date +\%Y\%m\%d).xlsx
```

---

## 🎯 Quick Start Checklist

- [ ] Clone repository
- [ ] Install Python dependencies
- [ ] Run `sudo bash deploy-service.sh`
- [ ] Access http://localhost:8501
- [ ] Login with admin/admin123
- [ ] Change default passwords
- [ ] Import your employee data
- [ ] Set up automated backups
- [ ] Configure firewall (optional)
- [ ] Set up HTTPS (production)

---

## 📞 Support

### Check Logs
```bash
# Application logs
tail -f streamlit.log

# Service logs
sudo journalctl -u ad-portal -f
```

### Common Issues
See `SERVICE_DEPLOYMENT.md` for detailed troubleshooting

### Service Commands
```bash
./service-manager.sh status    # Check status
sudo ./service-manager.sh restart  # Restart service
```

---

## 📄 License

See LICENSE file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Version**: 1.0.1  
**Last Updated**: October 16, 2025  
**Status**: Production Ready ✅
