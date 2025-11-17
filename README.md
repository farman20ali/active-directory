# 🚀 Active Directory Portal

A lightweight, Excel-backed employee directory management system built with Streamlit. Perfect for small to medium organizations needing a simple AD-like portal without complex infrastructure.

## ✨ Features

✅ **Role-Based Authentication** - Admin, Viewer, and Guest modes  
✅ **Employee Management** - Full CRUD operations with search & filters  
✅ **Department Management** - Sync, merge, rename, and delete departments  
✅ **Bulk Operations** - Upload Excel/CSV files with smart mapping  
✅ **Advanced Search** - Multi-column filters and global search  
✅ **Data Export** - Download filtered or complete data as CSV/Excel  
✅ **Auto-Deploy** - Systemd service with auto-path detection  
✅ **Audit Trail** - Track changes with timestamps  

## 🔑 Default Login Credentials

| Username | Password   | Role   | Access Level                |
|----------|------------|--------|-----------------------------|
| `admin`  | `admin123` | Admin  | Full create/edit/delete     |
| `viewer` | `viewer123` | Viewer | Read-only with save/export  |
| Guest    | No login   | Guest  | View-only mode              |

⚠️ **Security Note:** Change default passwords immediately in production!

---

## 🚀 Quick Start

### Option 1: Using Makefile (Recommended)

#### View all available commands:
```bash
make help
```

#### Install dependencies:
```bash
make install
```

#### Run locally for testing:
```bash
make run
```
Access at: **http://localhost:8501**

#### Deploy as systemd service:
```bash
sudo make deploy
sudo make start
```

#### Other useful commands:
```bash
make status      # Check service status
make logs        # View live logs
make restart     # Restart service
make stop        # Stop service
sudo make uninstall  # Remove service
```

---

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run Locally
```bash
streamlit run streamlit_ad_portal_app.py
```

#### 3. Deploy as Service (Optional)
```bash
sudo bash deploy-service.sh
```

Access the portal at: **http://localhost:8501**

---

## 🎯 Usage Guide

### 🔓 Guest Mode (No Login Required)
- ✅ View employee directory with pagination
- ✅ Search and filter across all fields
- ✅ View department information
- ✅ Export filtered data (CSV/Excel)
- ❌ Cannot add, edit, or delete records

### 👁️ Viewer Role (`viewer` / `viewer123`)
- ✅ All guest mode features
- ✅ Save/reload data from Excel
- ✅ Export complete user lists
- ✅ Access to file metrics
- ❌ Cannot modify any data

### 🔐 Admin Role (`admin` / `admin123`)
- ✅ All viewer features
- ✅ **Add/Edit/Delete** employees
- ✅ **Add/Edit/Delete** departments
- ✅ **Bulk upload** from Excel/CSV
- ✅ **Sync departments** from employee records
- ✅ **Merge/Rename** departments
- ✅ Activate all inactive users
- ✅ Access to audit logs and debug info

---

## 📁 Data Storage

All data is stored in **`employees.xlsx`** with 3 sheets:

| Sheet         | Purpose                                    |
|---------------|--------------------------------------------|
| **Employees** | Employee records (ID, name, dept, etc.)    |
| **Departments**| Department list with descriptions         |
| **Users**     | Login credentials (username, password, role)|

### Auto-Backup
- Backups are created automatically before bulk operations
- Location: `backups/` directory
- Format: `employees-backup-YYYYMMDD-HHMMSS.xlsx`

---

## 🛠️ Service Management

### Using Makefile Commands

```bash
# Check if service is running
make status

# View live logs
make logs

# Restart after code changes
make restart

# Stop the service
make stop

# Start the service
make start

# Remove service completely
sudo make uninstall
```

### Manual Service Commands

```bash
# Check status
sudo systemctl status ad-portal

# View logs
journalctl -u ad-portal -f

# Restart
sudo systemctl restart ad-portal

# Enable auto-start on boot
sudo systemctl enable ad-portal

# Disable auto-start
sudo systemctl disable ad-portal
```

---

## 🔒 Security & Best Practices

### Immediate Actions
1. ✅ **Change default passwords** in the Users sheet of `employees.xlsx`
2. ✅ **Backup `employees.xlsx`** regularly (contains all data)
3. ✅ **Set file permissions**: `chmod 600 employees.xlsx`
4. ✅ **Use HTTPS** in production environments

### Production Recommendations
- Consider implementing password hashing (bcrypt/argon2)
- Use environment variables for sensitive configs
- Set up regular automated backups
- Enable firewall rules to restrict access
- Use a reverse proxy (nginx/apache) with SSL
- Implement session timeout mechanisms

---

## 🆘 Troubleshooting

### Service Won't Start
```bash
# Check service status and logs
sudo systemctl status ad-portal
sudo journalctl -u ad-portal -n 50

# Check if port is already in use
sudo lsof -i :8501

# Restart the service
sudo systemctl restart ad-portal
```

### Port 8501 Already in Use
```bash
# Find process using the port
lsof -ti:8501

# Kill the process
lsof -ti:8501 | xargs kill -9

# Then restart service or app
make restart
```

### Excel File Locked
- Close Excel if you have the file open
- Check for zombie processes: `ps aux | grep streamlit`
- Verify file permissions: `ls -la employees.xlsx`

### Login Issues
- Check Users sheet in `employees.xlsx`
- Ensure credentials are **case-sensitive**
- Verify role is spelled correctly: `admin`, `viewer`, or `guest`
- Try reloading from Excel using the sidebar button

### Cross-Device Link Error
- Already fixed! The app uses `shutil.move()` for cross-filesystem compatibility
- If you still see this, ensure temp files have proper permissions

---

## � Project Structure

```
active-directory/
├── streamlit_ad_portal_app.py    # Main application
├── employees.xlsx                # Data storage (auto-created)
├── requirements.txt              # Python dependencies
├── Makefile                      # Quick commands
├── deploy-service.sh             # Auto-deploy script
├── uninstall-service.sh          # Service removal script
├── service-manager.sh            # Service control script
├── ad-portal.service.template    # Service template (for reference)
├── ad-portal.service             # Generated service file (not in git)
├── README.md                     # This file
├── CONFIGURATION.md              # Detailed config guide
├── SERVICE_DEPLOYMENT.md         # Service setup details
├── QUICK_REFERENCE.txt           # Command cheat sheet
├── bulk-upload.csv               # Sample bulk upload
├── sample_bulk_upload.csv        # Sample with headers
├── .gitignore                    # Git exclusions
└── backups/                      # Auto-generated backups
```

---

## 🚢 Deployment Options

### Local Development
```bash
make run
# or
streamlit run streamlit_ad_portal_app.py
```

### Linux Server (Systemd Service)
```bash
# One-time setup
sudo make deploy

# Start service
sudo make start

# Enable auto-start on boot
sudo systemctl enable ad-portal
```

### Docker (Coming Soon)
```bash
docker-compose up -d
```

### Cloud Deployment
- **AWS**: Deploy on EC2 with systemd or ECS
- **Google Cloud**: Use Compute Engine or Cloud Run
- **Azure**: Deploy on VM or App Service
- **DigitalOcean**: Use Droplets with systemd

---

## 📖 Additional Documentation

| File                      | Description                              |
|---------------------------|------------------------------------------|
| `CONFIGURATION.md`        | Detailed configuration options           |
| `SERVICE_DEPLOYMENT.md`   | Systemd service setup guide              |
| `QUICK_REFERENCE.txt`     | Command cheat sheet                      |
| `bulk-upload.csv`         | Sample bulk upload template              |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a pull request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 💡 Tips & Tricks

### Quick Access via Alias
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias adp-start='sudo systemctl start ad-portal'
alias adp-stop='sudo systemctl stop ad-portal'
alias adp-restart='sudo systemctl restart ad-portal'
alias adp-status='sudo systemctl status ad-portal'
alias adp-logs='tail -f /path/to/active-directory/streamlit.log'
```

### Bulk Upload Format
Download `sample_bulk_upload.csv` for the correct format:
- Include headers matching employee fields
- Map columns during upload
- Review preview before importing

### Department Sync
Use "Sync Departments" to:
- Find departments in employee records
- Add missing departments automatically
- Keep data consistent

---

## 🐛 Known Issues

- None at this time! 🎉

---

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review `QUICK_REFERENCE.txt` for commands

---

**Made with ❤️ for simplified employee management**

## 🔄 Updating Credentials

### Method 1: Via Excel
1. Stop the application
2. Open `employees.xlsx`
3. Go to "Users" sheet
4. Modify usernames/passwords/roles
5. Save and restart app

### Method 2: Programmatically
```python
import pandas as pd

# Read Excel
xls = pd.read_excel('employees.xlsx', sheet_name='Users')

# Add new user
new_user = {
    'Username': 'newadmin',
    'Password': 'secure_password_123',
    'Role': 'admin',
    'Full Name': 'New Administrator',
    'Created Date': pd.Timestamp.now().isoformat()
}

# Append and save
xls = pd.concat([xls, pd.DataFrame([new_user])], ignore_index=True)

# Save back
with pd.ExcelWriter('employees.xlsx', mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
    xls.to_excel(writer, sheet_name='Users', index=False)
```

## 🎨 Customization

### Change Port
```bash
streamlit run streamlit_ad_portal_app.py --server.port 8080
```

### Change Theme
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 💡 Tips & Tricks

1. **Quick Search** - Use the search bar at the top to search across all fields
2. **Bulk Upload** - Prepare Excel/CSV with matching column names
3. **Department Sync** - Automatically detect missing departments
4. **Export Filtered** - Apply filters first, then export
5. **Keyboard Shortcuts** - Use Tab to navigate forms quickly

## 🐛 Known Limitations

- Passwords stored in plain text (consider hashing for production)
- Single-user edits (no concurrent editing protection)  
- Excel-based storage (consider database for large scale)
- No audit log for changes (add if needed)

## 📞 Support

For issues or questions:
1. Check `DEPLOYMENT_GUIDE.md`
2. Review error logs in terminal
3. Verify Excel file isn't corrupted
4. Ensure all dependencies are installed

## 🔐 Production Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Set up HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Implement password hashing
- [ ] Add session timeout
- [ ] Configure proper file permissions
- [ ] Set up monitoring/logging
- [ ] Test disaster recovery
- [ ] Document admin procedures

## 📦 Project Structure

```
active-directory/
├── streamlit_ad_portal_app.py  # Main application
├── requirements.txt             # Python dependencies
├── employees.xlsx              # Data storage (auto-created)
├── DEPLOYMENT_GUIDE.md         # Full deployment docs
└── README.md                   # This file
```

## 🚀 Next Steps

1. **Test the application** - Try all features with different roles
2. **Customize credentials** - Update default passwords
3. **Import your data** - Use bulk upload or Excel import
4. **Deploy** - Follow DEPLOYMENT_GUIDE.md for production

---

**Made with ❤️ using Streamlit**
