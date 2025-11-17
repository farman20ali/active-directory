# 📘 Makefile Quick Guide

This project includes a Makefile for simplified management of the Active Directory Portal.

## 🚀 Quick Start

```bash
# View all available commands
make help

# Install Python dependencies
make install

# Run locally for development/testing
make run
```

## 📋 Available Commands

### Installation
```bash
make install        # Install Python dependencies from requirements.txt
```

### Service Deployment
```bash
sudo make deploy    # Deploy as systemd service (auto-detects paths)
sudo make start     # Start the service
sudo make stop      # Stop the service
sudo make restart   # Restart the service
make status         # Check service status
make logs           # View live service logs (Ctrl+C to exit)
sudo make uninstall # Remove systemd service completely
```

### Development
```bash
make run            # Run locally without installing as service
make clean          # Clean temporary files, logs, and generated files
```

## 💡 How It Works

### Auto-Detection
The Makefile works with the deployment scripts to:
- ✅ Auto-detect project directory
- ✅ Auto-detect current user
- ✅ Auto-detect Streamlit installation path
- ✅ Generate service file with correct paths

### No Hardcoded Paths
Unlike traditional setups, this Makefile:
- ❌ No hardcoded usernames
- ❌ No hardcoded paths
- ❌ No manual configuration needed
- ✅ Works on any Linux system
- ✅ Safe for version control

## 🎯 Common Workflows

### First Time Setup
```bash
# 1. Install dependencies
make install

# 2. Test locally first
make run
# (Access http://localhost:8501, then Ctrl+C to stop)

# 3. Deploy as service
sudo make deploy

# 4. Start the service
sudo make start

# 5. Check it's running
make status
```

### Daily Use
```bash
# Check if service is running
make status

# View logs
make logs

# Restart after changes
sudo make restart
```

### Troubleshooting
```bash
# View live logs for debugging
make logs

# Check service status with details
make status

# Clean and restart
make clean
sudo make restart
```

### Removing Service
```bash
# Stop and remove service
sudo make uninstall

# Clean generated files
make clean
```

## 🔄 Comparison with Other Methods

### Using Makefile (Recommended)
```bash
sudo make deploy    # One command to deploy
make status         # Easy to remember
make logs           # Simple log viewing
```

### Using Shell Scripts
```bash
sudo bash deploy-service.sh              # Longer command
./service-manager.sh status              # Need to remember script name
sudo journalctl -u ad-portal -f          # Complex log command
```

### Using Systemctl Directly
```bash
sudo systemctl start ad-portal           # Must know service name
sudo systemctl status ad-portal          # Verbose commands
sudo journalctl -u ad-portal -f          # Complex syntax
```

## 📝 Notes

- Most commands work without sudo except `deploy`, `start`, `stop`, `restart`, and `uninstall`
- The `deploy` command calls `deploy-service.sh` internally
- The `uninstall` command calls `uninstall-service.sh` internally
- Logs are written to `streamlit.log` in the project directory
- Service is named `ad-portal` in systemd

## 🎨 Customization

To modify Makefile behavior, edit the `Makefile` in the project root. The file is well-commented and easy to customize.

## 💾 Version Control

The Makefile is tracked in Git, but the generated `ad-portal.service` file is not (it's in `.gitignore`). This means:
- ✅ Makefile is shared across developers
- ✅ No hardcoded paths in Git
- ✅ Each deployment generates its own service file
- ✅ Portable across different systems

## 🆘 Help

For more information:
```bash
make help           # View all commands
cat README.md       # Full documentation
cat QUICK_REFERENCE.txt  # Command cheat sheet
```
