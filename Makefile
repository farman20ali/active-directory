.PHONY: help install deploy start stop restart status logs uninstall clean

# Default target
help:
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  Active Directory Portal - Makefile Commands"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "  📦 Installation:"
	@echo "    make install        Install Python dependencies"
	@echo ""
	@echo "  🚀 Service Deployment:"
	@echo "    make deploy         Deploy as systemd service (requires sudo)"
	@echo "    make start          Start the service"
	@echo "    make stop           Stop the service"
	@echo "    make restart        Restart the service"
	@echo "    make status         Check service status"
	@echo "    make logs           View service logs (live tail)"
	@echo "    make uninstall      Remove systemd service (requires sudo)"
	@echo ""
	@echo "  💻 Development:"
	@echo "    make run            Run locally (without service)"
	@echo "    make clean          Clean temporary files and logs"
	@echo ""
	@echo "  ℹ️  Note: Service commands require sudo privileges"
	@echo "═══════════════════════════════════════════════════════════"

# Install Python dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Deploy as systemd service
deploy:
	@echo "🚀 Deploying AD Portal as systemd service..."
	@if [ "$$EUID" -ne 0 ]; then \
		echo "⚠️  This command requires sudo privileges"; \
		echo "Run: sudo make deploy"; \
		exit 1; \
	fi
	bash deploy-service.sh
	@echo "✅ Service deployed successfully!"

# Start the service
start:
	@echo "▶️  Starting AD Portal service..."
	sudo systemctl start ad-portal
	@sleep 2
	@sudo systemctl status ad-portal --no-pager
	@echo ""
	@echo "✅ Service started! Access at: http://localhost:8501"

# Stop the service
stop:
	@echo "⏹️  Stopping AD Portal service..."
	sudo systemctl stop ad-portal
	@echo "✅ Service stopped!"

# Restart the service
restart:
	@echo "🔄 Restarting AD Portal service..."
	sudo systemctl restart ad-portal
	@sleep 2
	@sudo systemctl status ad-portal --no-pager
	@echo ""
	@echo "✅ Service restarted!"

# Check service status
status:
	@sudo systemctl status ad-portal --no-pager

# View logs (live tail)
logs:
	@echo "📋 Viewing AD Portal logs (Ctrl+C to exit)..."
	@if [ -f streamlit.log ]; then \
		tail -f streamlit.log; \
	else \
		echo "❌ Log file not found. Service may not be running yet."; \
	fi

# Uninstall service
uninstall:
	@echo "🗑️  Uninstalling AD Portal service..."
	@if [ "$$EUID" -ne 0 ]; then \
		echo "⚠️  This command requires sudo privileges"; \
		echo "Run: sudo make uninstall"; \
		exit 1; \
	fi
	bash uninstall-service.sh
	@echo "✅ Service uninstalled successfully!"

# Run locally without service
run:
	@echo "💻 Running AD Portal locally..."
	@echo "Access at: http://localhost:8501"
	@echo "Press Ctrl+C to stop"
	streamlit run streamlit_ad_portal_app.py

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	rm -rf __pycache__/
	rm -f *.pyc
	rm -f *.log
	rm -f ad-portal.service
	@echo "✅ Cleanup complete!"
