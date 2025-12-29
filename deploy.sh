#!/bin/bash

# =============================================================================
# Pizza Store Backend - Production Deployment Script
# =============================================================================
# 
# This script sets up a complete production environment on DigitalOcean Droplet
# 
# Usage:
#   1. SSH into your droplet: ssh root@your-droplet-ip
#   2. Upload this script: scp deploy.sh root@your-droplet-ip:/root/
#   3. Make executable: chmod +x deploy.sh
#   4. Run: ./deploy.sh
#
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# =============================================================================

# Application Settings
APP_NAME="pizza-store"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/pizza-store-backend"
DOMAIN="api.marinapizzas.com.au"

# Git Repository (update with your repo)
GIT_REPO="git@github.com:Ali-oss-cell/pizza_store_backend_au.git"

# Python version
PYTHON_VERSION="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}=============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use sudo)"
        exit 1
    fi
}

# =============================================================================
# STEP 1: SYSTEM UPDATE & BASIC PACKAGES
# =============================================================================

setup_system() {
    print_header "Step 1: System Update & Basic Packages"
    
    print_info "Updating system packages..."
    apt update && apt upgrade -y
    
    print_info "Installing essential packages..."
    apt install -y \
        ${PYTHON_VERSION} \
        ${PYTHON_VERSION}-pip \
        ${PYTHON_VERSION}-venv \
        ${PYTHON_VERSION}-dev \
        nginx \
        git \
        curl \
        wget \
        unzip \
        htop \
        supervisor \
        libpq-dev \
        build-essential \
        certbot \
        python3-certbot-nginx \
        ufw \
        fail2ban \
        logrotate
    
    print_success "System packages installed"
}

# =============================================================================
# STEP 2: FIREWALL CONFIGURATION (UFW)
# =============================================================================

setup_firewall() {
    print_header "Step 2: Firewall Configuration (UFW)"
    
    print_info "Configuring UFW firewall..."
    
    # Reset UFW to default
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (important! Don't lock yourself out)
    ufw allow 22/tcp comment 'SSH'
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Allow Nginx
    ufw allow 'Nginx Full'
    
    # Enable UFW
    ufw --force enable
    
    print_success "Firewall configured and enabled"
    
    # Show status
    ufw status verbose
}

# =============================================================================
# STEP 3: FAIL2BAN CONFIGURATION (Brute Force Protection)
# =============================================================================

setup_fail2ban() {
    print_header "Step 3: Fail2Ban Configuration (Brute Force Protection)"
    
    print_info "Configuring Fail2Ban..."
    
    # Create jail.local configuration
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban hosts for 1 hour
bantime = 3600

# Find time (10 minutes)
findtime = 600

# Max retries before ban
maxretry = 5

# Ignore local IPs
ignoreip = 127.0.0.1/8 ::1

# Use systemd backend
backend = systemd

# Send email alerts (optional - configure later for Twilio)
# destemail = your-email@example.com
# sendername = Fail2Ban
# mta = sendmail

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

    # Restart Fail2Ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    print_success "Fail2Ban configured and enabled"
}

# =============================================================================
# STEP 4: CREATE APPLICATION DIRECTORY & USER
# =============================================================================

setup_app_directory() {
    print_header "Step 4: Setting Up Application Directory"
    
    print_info "Creating application directory..."
    mkdir -p ${APP_DIR}
    
    print_info "Setting up directory structure..."
    mkdir -p ${APP_DIR}/logs
    mkdir -p ${APP_DIR}/static
    mkdir -p ${APP_DIR}/media
    
    print_success "Application directory created: ${APP_DIR}"
}

# =============================================================================
# STEP 5: CLONE REPOSITORY
# =============================================================================

clone_repository() {
    print_header "Step 5: Clone Repository"
    
    # Check if directory already has content
    if [ -d "${APP_DIR}/.git" ]; then
        print_info "Repository already exists, pulling latest changes..."
        cd ${APP_DIR}
        git pull
    else
        print_info "Cloning repository..."
        
        # If SSH key exists, use SSH, otherwise prompt for HTTPS
        if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
            git clone ${GIT_REPO} ${APP_DIR}
        else
            print_warning "No SSH key found. You may need to:"
            print_info "1. Generate SSH key: ssh-keygen -t ed25519"
            print_info "2. Add to GitHub: cat ~/.ssh/id_ed25519.pub"
            print_info "3. Or use HTTPS: git clone https://github.com/Ali-oss-cell/pizza_store_backend_au.git ${APP_DIR}"
            
            read -p "Press Enter after setting up Git access, or Ctrl+C to exit..."
            git clone ${GIT_REPO} ${APP_DIR}
        fi
    fi
    
    cd ${APP_DIR}
    print_success "Repository cloned/updated"
}

# =============================================================================
# STEP 6: PYTHON VIRTUAL ENVIRONMENT
# =============================================================================

setup_python_env() {
    print_header "Step 6: Python Virtual Environment"
    
    cd ${APP_DIR}
    
    print_info "Creating virtual environment..."
    ${PYTHON_VERSION} -m venv venv
    
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment set up"
}

# =============================================================================
# STEP 7: ENVIRONMENT FILE SETUP
# =============================================================================

setup_env_file() {
    print_header "Step 7: Environment File Setup"
    
    cd ${APP_DIR}
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " overwrite
        if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    print_info "Creating .env file..."
    
    # Get droplet IP
    DROPLET_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    
    print_info "Generating Django secret key..."
    source venv/bin/activate
    SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # Create .env file with all values
    cat > .env << EOF
# Django Production Environment Variables
# DO NOT commit this file to git!

# ============================================
# SECURITY SETTINGS
# ============================================

# Secret Key - Auto-generated
DJANGO_SECRET_KEY=${SECRET_KEY}

# Debug Mode - MUST be False in production
DEBUG=False

# Allowed Hosts - Comma-separated list of domains/IPs
ALLOWED_HOSTS=api.marinapizzas.com.au,marinapizzas.com.au,www.marinapizzas.com.au,${DROPLET_IP}

# ============================================
# DATABASE CONFIGURATION (DigitalOcean Managed PostgreSQL)
# ============================================

DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=AVNS_1GHB72K7lqTFT0MS372
DB_HOST=private-db-postgresql-syd1-42296-do-user-26523274-0.e.db.ondigitalocean.com
DB_PORT=25060

# SSL Mode for PostgreSQL (required for DigitalOcean managed databases)
DB_SSLMODE=require

# ============================================
# CORS CONFIGURATION
# ============================================

# CORS Allowed Origins - Comma-separated list of frontend URLs
CORS_ALLOWED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au

# CSRF Trusted Origins - Comma-separated list of trusted domains
CSRF_TRUSTED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au,https://api.marinapizzas.com.au

# ============================================
# SSL/SECURITY SETTINGS (only used when DEBUG=False)
# ============================================

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT=True

# HSTS (HTTP Strict Transport Security) - 1 year
SECURE_HSTS_SECONDS=31536000
EOF

    # Protect the file
    chmod 600 .env
    
    print_success ".env file created with:"
    print_info "  - Auto-generated SECRET_KEY"
    print_info "  - Droplet IP: ${DROPLET_IP}"
    print_info "  - Database credentials configured"
    print_info "  - Domain names configured"
    
    print_warning "Verify database password is correct in .env file"
    read -p "Press Enter to continue (or Ctrl+C to edit .env first)..."
    
    print_success "Environment file configured"
}

# =============================================================================
# STEP 8: DJANGO SETUP
# =============================================================================

setup_django() {
    print_header "Step 8: Django Setup"
    
    cd ${APP_DIR}/pizza_store
    source ../venv/bin/activate
    
    print_info "Running database migrations..."
    python manage.py migrate --noinput
    
    print_info "Collecting static files..."
    python manage.py collectstatic --noinput
    
    print_info "Checking Django configuration..."
    python manage.py check
    
    print_warning "Do you want to create a superuser now?"
    read -p "Create superuser? (y/N): " create_super
    if [ "$create_super" = "y" ] || [ "$create_super" = "Y" ]; then
        python manage.py createsuperuser
    fi
    
    print_success "Django setup complete"
}

# =============================================================================
# STEP 9: GUNICORN CONFIGURATION
# =============================================================================

setup_gunicorn() {
    print_header "Step 9: Gunicorn Configuration"
    
    print_info "Creating Gunicorn systemd service..."
    
    cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Pizza Store Gunicorn daemon
After=network.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}/pizza_store
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/gunicorn \\
    --access-logfile ${APP_DIR}/logs/gunicorn-access.log \\
    --error-logfile ${APP_DIR}/logs/gunicorn-error.log \\
    --workers 3 \\
    --bind unix:/run/${APP_NAME}.sock \\
    --timeout 120 \\
    pizza_store.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    print_info "Creating socket directory..."
    
    # Create tmpfiles.d config for socket directory persistence
    cat > /etc/tmpfiles.d/${APP_NAME}.conf << EOF
d /run/${APP_NAME} 0755 ${APP_USER} ${APP_GROUP} -
EOF

    print_info "Reloading systemd daemon..."
    systemctl daemon-reload
    
    print_info "Starting Gunicorn service..."
    systemctl start ${APP_NAME}
    systemctl enable ${APP_NAME}
    
    # Wait for socket to be created
    sleep 2
    
    # Check if socket exists
    if [ -S "/run/${APP_NAME}.sock" ]; then
        print_success "Gunicorn service started and socket created"
    else
        print_warning "Socket not found, checking service status..."
        systemctl status ${APP_NAME}
    fi
    
    print_success "Gunicorn configured"
}

# =============================================================================
# STEP 10: NGINX CONFIGURATION
# =============================================================================

setup_nginx() {
    print_header "Step 10: Nginx Configuration"
    
    print_info "Creating Nginx configuration..."
    
    cat > /etc/nginx/sites-available/${APP_NAME} << EOF
# Rate limiting zone
limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    server_name ${DOMAIN};

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Max upload size
    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/${APP_NAME}-access.log;
    error_log /var/log/nginx/${APP_NAME}-error.log;

    # GraphQL endpoint with rate limiting
    location /graphql/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://unix:/run/${APP_NAME}.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Admin panel
    location /admin/ {
        limit_req zone=api_limit burst=5 nodelay;
        
        proxy_pass http://unix:/run/${APP_NAME}.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias ${APP_DIR}/pizza_store/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # Gzip static files
        gzip_static on;
    }

    # Media files
    location /media/ {
        alias ${APP_DIR}/pizza_store/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Default location
    location / {
        proxy_pass http://unix:/run/${APP_NAME}.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check endpoint
    location /health/ {
        return 200 'OK';
        add_header Content-Type text/plain;
    }

    # Block common attack patterns
    location ~* /(\.git|\.env|\.htaccess|wp-admin|wp-login|xmlrpc\.php) {
        return 404;
    }
}
EOF

    print_info "Enabling site..."
    ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
    
    print_info "Removing default site..."
    rm -f /etc/nginx/sites-enabled/default
    
    print_info "Testing Nginx configuration..."
    nginx -t
    
    print_info "Restarting Nginx..."
    systemctl restart nginx
    systemctl enable nginx
    
    print_success "Nginx configured"
}

# =============================================================================
# STEP 11: SSL CERTIFICATE (Let's Encrypt)
# =============================================================================

setup_ssl() {
    print_header "Step 11: SSL Certificate (Let's Encrypt)"
    
    print_warning "Before proceeding, ensure:"
    print_info "1. Domain ${DOMAIN} is pointing to this server's IP"
    print_info "2. DNS has propagated (can take up to 48 hours)"
    print_info ""
    
    read -p "Is DNS configured and propagated? (y/N): " dns_ready
    
    if [ "$dns_ready" = "y" ] || [ "$dns_ready" = "Y" ]; then
        print_info "Obtaining SSL certificate..."
        certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN} --redirect
        
        print_info "Setting up auto-renewal..."
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        
        print_success "SSL certificate installed and auto-renewal configured"
    else
        print_warning "Skipping SSL setup. Run later with:"
        print_info "sudo certbot --nginx -d ${DOMAIN}"
    fi
}

# =============================================================================
# STEP 12: LOG ROTATION
# =============================================================================

setup_logrotate() {
    print_header "Step 12: Log Rotation Configuration"
    
    print_info "Creating logrotate configuration..."
    
    cat > /etc/logrotate.d/${APP_NAME} << EOF
${APP_DIR}/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ${APP_USER} ${APP_GROUP}
    sharedscripts
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/${APP_NAME}-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ${APP_USER} adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 \$(cat /var/run/nginx.pid)
    endscript
}
EOF

    print_success "Log rotation configured"
}

# =============================================================================
# STEP 13: SET PERMISSIONS
# =============================================================================

set_permissions() {
    print_header "Step 13: Setting File Permissions"
    
    print_info "Setting ownership..."
    chown -R ${APP_USER}:${APP_GROUP} ${APP_DIR}
    
    print_info "Setting directory permissions..."
    find ${APP_DIR} -type d -exec chmod 755 {} \;
    
    print_info "Setting file permissions..."
    find ${APP_DIR} -type f -exec chmod 644 {} \;
    
    print_info "Setting executable permissions for scripts..."
    chmod +x ${APP_DIR}/venv/bin/*
    chmod 755 ${APP_DIR}/deploy.sh 2>/dev/null || true
    
    print_info "Setting media directory permissions..."
    chmod 775 ${APP_DIR}/pizza_store/media
    
    print_info "Protecting .env file..."
    chmod 600 ${APP_DIR}/.env
    
    print_success "Permissions configured"
}

# =============================================================================
# STEP 14: SECURITY HARDENING
# =============================================================================

security_hardening() {
    print_header "Step 14: Security Hardening"
    
    print_info "Configuring SSH security..."
    
    # Backup original SSH config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # SSH hardening (keeping password auth for now, can disable later)
    sed -i 's/#PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
    sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config
    sed -i 's/X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config
    
    print_info "Restarting SSH..."
    systemctl restart sshd
    
    print_info "Setting up automatic security updates..."
    apt install -y unattended-upgrades
    dpkg-reconfigure -plow unattended-upgrades
    
    print_success "Security hardening complete"
}

# =============================================================================
# STEP 15: CREATE MANAGEMENT SCRIPTS
# =============================================================================

create_management_scripts() {
    print_header "Step 15: Creating Management Scripts"
    
    # Restart script
    cat > ${APP_DIR}/restart.sh << 'EOF'
#!/bin/bash
echo "Restarting Pizza Store services..."
sudo systemctl restart pizza-store
sudo systemctl restart nginx
echo "Services restarted!"
sudo systemctl status pizza-store --no-pager
EOF
    chmod +x ${APP_DIR}/restart.sh
    
    # Update script
    cat > ${APP_DIR}/update.sh << 'EOF'
#!/bin/bash
echo "Updating Pizza Store..."
cd /var/www/pizza-store-backend

echo "Pulling latest changes..."
git pull

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
cd pizza_store
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Restarting services..."
sudo systemctl restart pizza-store
sudo systemctl restart nginx

echo "Update complete!"
EOF
    chmod +x ${APP_DIR}/update.sh
    
    # Status script
    cat > ${APP_DIR}/status.sh << 'EOF'
#!/bin/bash
echo "=== Pizza Store Status ==="
echo ""
echo "--- Gunicorn Service ---"
sudo systemctl status pizza-store --no-pager | head -20
echo ""
echo "--- Nginx Service ---"
sudo systemctl status nginx --no-pager | head -10
echo ""
echo "--- Disk Usage ---"
df -h /
echo ""
echo "--- Memory Usage ---"
free -h
echo ""
echo "--- Recent Logs ---"
sudo tail -10 /var/www/pizza-store-backend/logs/gunicorn-error.log 2>/dev/null || echo "No error logs"
EOF
    chmod +x ${APP_DIR}/status.sh
    
    # Logs script
    cat > ${APP_DIR}/logs.sh << 'EOF'
#!/bin/bash
echo "=== Pizza Store Logs ==="
echo "1. Gunicorn Access Log"
echo "2. Gunicorn Error Log"
echo "3. Nginx Access Log"
echo "4. Nginx Error Log"
echo "5. All Gunicorn Logs (live)"
read -p "Select option (1-5): " option

case $option in
    1) tail -f /var/www/pizza-store-backend/logs/gunicorn-access.log ;;
    2) tail -f /var/www/pizza-store-backend/logs/gunicorn-error.log ;;
    3) tail -f /var/log/nginx/pizza-store-access.log ;;
    4) tail -f /var/log/nginx/pizza-store-error.log ;;
    5) journalctl -u pizza-store -f ;;
    *) echo "Invalid option" ;;
esac
EOF
    chmod +x ${APP_DIR}/logs.sh
    
    # Backup script (for future use)
    cat > ${APP_DIR}/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/pizza-store"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Backing up media files..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/pizza-store-backend/pizza_store/media

echo "Backup complete: $BACKUP_DIR"
ls -la $BACKUP_DIR
EOF
    chmod +x ${APP_DIR}/backup.sh
    
    chown -R ${APP_USER}:${APP_GROUP} ${APP_DIR}/*.sh
    
    print_success "Management scripts created"
    print_info "Available scripts:"
    print_info "  ${APP_DIR}/restart.sh - Restart services"
    print_info "  ${APP_DIR}/update.sh  - Update application"
    print_info "  ${APP_DIR}/status.sh  - Check status"
    print_info "  ${APP_DIR}/logs.sh    - View logs"
    print_info "  ${APP_DIR}/backup.sh  - Backup media"
}

# =============================================================================
# STEP 16: FINAL CHECKS & SUMMARY
# =============================================================================

final_checks() {
    print_header "Step 16: Final Checks & Summary"
    
    echo ""
    print_info "Checking services..."
    
    # Check Gunicorn
    if systemctl is-active --quiet ${APP_NAME}; then
        print_success "Gunicorn is running"
    else
        print_error "Gunicorn is NOT running"
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Nginx is NOT running"
    fi
    
    # Check UFW
    if ufw status | grep -q "active"; then
        print_success "Firewall (UFW) is active"
    else
        print_warning "Firewall (UFW) is NOT active"
    fi
    
    # Check Fail2Ban
    if systemctl is-active --quiet fail2ban; then
        print_success "Fail2Ban is running"
    else
        print_warning "Fail2Ban is NOT running"
    fi
    
    # Test HTTP endpoint
    echo ""
    print_info "Testing HTTP endpoint..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        print_success "HTTP endpoint responding (status: ${HTTP_STATUS})"
    else
        print_warning "HTTP endpoint returned status: ${HTTP_STATUS}"
    fi
    
    echo ""
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}  DEPLOYMENT COMPLETE!${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    print_info "Application URL: http://${DOMAIN}/"
    print_info "GraphQL Endpoint: http://${DOMAIN}/graphql/"
    print_info "Admin Panel: http://${DOMAIN}/admin/"
    echo ""
    print_warning "Next Steps:"
    echo "  1. Verify DNS is pointing to this server"
    echo "  2. Run SSL setup: sudo certbot --nginx -d ${DOMAIN}"
    echo "  3. Test the API endpoint"
    echo "  4. Create admin user if not done: cd ${APP_DIR}/pizza_store && source ../venv/bin/activate && python manage.py createsuperuser"
    echo ""
    print_info "Useful Commands:"
    echo "  Restart:  sudo systemctl restart ${APP_NAME}"
    echo "  Logs:     sudo journalctl -u ${APP_NAME} -f"
    echo "  Status:   sudo systemctl status ${APP_NAME}"
    echo "  Update:   ${APP_DIR}/update.sh"
    echo ""
    print_info "Firewall Status:"
    ufw status
    echo ""
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    clear
    echo ""
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}  Pizza Store Backend Deployment Script${NC}"
    echo -e "${GREEN}  Domain: ${DOMAIN}${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    
    check_root
    
    print_warning "This script will:"
    echo "  - Update system packages"
    echo "  - Install Nginx, Gunicorn, and dependencies"
    echo "  - Configure firewall (UFW)"
    echo "  - Set up Fail2Ban for brute force protection"
    echo "  - Clone and set up the application"
    echo "  - Configure SSL (optional)"
    echo ""
    
    read -p "Continue with deployment? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    # Run all steps
    setup_system
    setup_firewall
    setup_fail2ban
    setup_app_directory
    clone_repository
    setup_python_env
    setup_env_file
    setup_django
    setup_gunicorn
    setup_nginx
    setup_ssl
    setup_logrotate
    set_permissions
    security_hardening
    create_management_scripts
    final_checks
}

# Run main function
main "$@"

