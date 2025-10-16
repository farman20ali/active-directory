# 🚀 Active Directory Portal - Quick Start

## ✨ Features

✅ **Login System** - Secure authentication with admin and viewer roles  
✅ **Guest Mode** - View employees without login  
✅ **Employee Management** - Full CRUD operations (Admin only)  
✅ **Department Management** - Sync, merge, rename departments  
✅ **Bulk Operations** - Upload Excel/CSV files  
✅ **Advanced Search** - Filter across all fields  
✅ **Export Data** - Download as CSV or Excel  

## 🔑 Default Login Credentials

| Username | Password   | Role   | Access                      |
|----------|------------|--------|-----------------------------|
| `admin`  | `admin123` | Admin  | Full create/edit/delete     |
| `viewer` | `viewer123` | Viewer | Read-only access            |

⚠️ **Change these passwords immediately in production!**

## 🏃 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_ad_portal_app.py
```

###  3. Open in Browser
Navigate to: **http://localhost:8501**

## 🎯 Usage Guide

### Guest Mode (No Login)
- ✅ View employee directory
- ✅ Search and filter employees
- ✅ View departments
- ✅ Export data
- ❌ Cannot add/edit/delete

### Viewer Role
- ✅ All guest features
- ✅ Save/reload Excel
- ✅ Export user lists
- ❌ Cannot modify data

### Admin Role
- ✅ All viewer features
- ✅ Add/edit/delete employees
- ✅ Add/edit/delete departments
- ✅ Bulk upload users
- ✅ Sync departments
- ✅ Activate all inactive users

## 📁 Data Storage

All data is stored in `employees.xlsx` with 3 sheets:
- **Employees** - Employee records
- **Departments** - Department list
- **Users** - Login credentials

## 🔒 Security Tips

1. **Change default passwords** in the Users sheet
2. **Backup regularly** - `employees.xlsx` contains all data
3. **File permissions** - Restrict access to the Excel file
4. **Use HTTPS** in production
5. **Consider password hashing** for production use

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Find and kill process
lsof -ti:8501 | xargs kill -9
# Then restart
streamlit run streamlit_ad_portal_app.py
```

**Excel file locked?**
- Close Excel if you have it open
- Check file permissions

**Login not working?**
- Check the Users sheet in `employees.xlsx`
- Ensure credentials match exactly (case-sensitive)

## 📖 Full Documentation

See `DEPLOYMENT_GUIDE.md` for:
- Production deployment instructions
- Docker setup
- Nginx reverse proxy configuration
- SSL/HTTPS setup
- Systemd service configuration
- Security hardening

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
