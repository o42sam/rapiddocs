#!/bin/bash

# DocGen VPS Initial Setup Script
# Run this script on a fresh Ubuntu 22.04 VPS to set up the environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="docgen"
APP_DIR="/home/docgen"
DOMAIN="api.rapiddocs.io"  # Change to your domain
EMAIL="admin@rapiddocs.io"  # Change to your email for SSL certificates

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
       log_error "This script must be run as root (use sudo)"
       exit 1
    fi
}

# Update system
update_system() {
    log_step "Updating system packages..."

    apt update
    apt upgrade -y
    apt autoremove -y

    log_info "System updated"
}

# Install required system packages
install_system_packages() {
    log_step "Installing system packages..."

    # Note: We do NOT install python3-pip globally to avoid
    # "externally managed environment" issues on Ubuntu 23.04+
    apt install -y \
        python3 \
        python3-venv \
        python3-dev \
        build-essential \
        git \
        nginx \
        certbot \
        python3-certbot-nginx \
        supervisor \
        postgresql \
        postgresql-contrib \
        redis-server \
        ufw \
        htop \
        ncdu \
        curl \
        wget \
        vim \
        tmux \
        fail2ban \
        unattended-upgrades

    log_info "System packages installed"
}

# Configure firewall
setup_firewall() {
    log_step "Configuring firewall..."

    # Reset UFW
    ufw --force reset

    # Default policies
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH (change port if using non-standard)
    ufw allow 22/tcp comment 'SSH'

    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'

    # Enable firewall
    ufw --force enable

    log_info "Firewall configured"
}

# Create application user
create_app_user() {
    log_step "Creating application user..."

    # Check if user exists
    if id "$APP_USER" &>/dev/null; then
        log_warn "User $APP_USER already exists"
    else
        # Create user with home directory
        useradd -m -s /bin/bash $APP_USER

        # Add to www-data group for Nginx
        usermod -a -G www-data $APP_USER

        log_info "User $APP_USER created"
    fi

    # Create application directories
    mkdir -p $APP_DIR/backend
    mkdir -p $APP_DIR/uploads
    mkdir -p $APP_DIR/generated_pdfs
    mkdir -p /var/log/docgen
    mkdir -p /var/run/docgen
    mkdir -p /tmp/docgen-uploads

    # Set ownership
    chown -R $APP_USER:$APP_USER $APP_DIR
    chown -R $APP_USER:$APP_USER /var/log/docgen
    chown -R $APP_USER:$APP_USER /var/run/docgen
    chown -R $APP_USER:$APP_USER /tmp/docgen-uploads

    # Set permissions
    chmod 755 $APP_DIR/uploads
    chmod 755 $APP_DIR/generated_pdfs

    log_info "Application directories created"
}

# Install Python dependencies
setup_python() {
    log_step "Setting up Python environment..."

    # Create a virtual environment for system tools to avoid
    # "externally managed environment" error on Ubuntu 23.04+
    log_info "Creating virtual environment for application..."

    # Switch to app user for Python setup
    su - $APP_USER << 'EOF'
cd /home/docgen/backend
python3 -m venv venv
source venv/bin/activate

# Upgrade pip within virtual environment
python -m pip install --upgrade pip

# Install required Python packages in venv
pip install gunicorn uvicorn[standard] supervisor

# Deactivate for now
deactivate
EOF

    # For system-wide tools, use apt or pipx
    apt install -y python3-pip 2>/dev/null || true

    # If pipx is available, use it for system tools
    if command -v pipx &> /dev/null; then
        pipx install supervisor
    fi

    log_info "Python environment configured (using virtual environment)"
}

# Configure MongoDB (using cloud MongoDB Atlas)
setup_mongodb_client() {
    log_step "Installing MongoDB client tools..."

    # Install MongoDB client for backups
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    apt update
    apt install -y mongodb-mongosh mongodb-database-tools

    log_info "MongoDB client tools installed"
}

# Configure Nginx
setup_nginx() {
    log_step "Configuring Nginx..."

    # Remove default site
    rm -f /etc/nginx/sites-enabled/default

    # Create cache directories
    mkdir -p /var/cache/nginx/docgen
    mkdir -p /var/cache/nginx/client_temp

    # Set permissions
    chown -R www-data:www-data /var/cache/nginx

    # Configure Nginx main settings
    cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
    multi_accept on;
    use epoll;
}

http {
    ##
    # Basic Settings
    ##
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 10M;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ##
    # SSL Settings
    ##
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    ##
    # Logging Settings
    ##
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    ##
    # Gzip Settings
    ##
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml application/atom+xml image/svg+xml text/javascript application/vnd.ms-fontobject application/x-font-ttf font/opentype;

    ##
    # Virtual Host Configs
    ##
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

    # Test configuration
    nginx -t

    # Restart Nginx
    systemctl restart nginx

    log_info "Nginx configured"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log_step "Setting up SSL certificates..."

    # Check if domain is provided
    if [ "$DOMAIN" = "api.rapiddocs.io" ]; then
        log_warn "Using default domain. Update DOMAIN variable in this script for your domain."
        read -p "Enter your domain (e.g., api.yourdomain.com): " DOMAIN
    fi

    if [ "$EMAIL" = "admin@rapiddocs.io" ]; then
        read -p "Enter your email for SSL notifications: " EMAIL
    fi

    # Create webroot directory for certbot
    mkdir -p /var/www/certbot
    chown www-data:www-data /var/www/certbot

    # Create temporary Nginx config for certbot
    cat > /etc/nginx/sites-available/certbot-temp << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 404;
    }
}
EOF

    # Enable temporary config
    ln -sf /etc/nginx/sites-available/certbot-temp /etc/nginx/sites-enabled/
    systemctl reload nginx

    # Obtain SSL certificate
    certbot certonly \
        --webroot \
        --webroot-path /var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        -d $DOMAIN

    # Remove temporary config
    rm -f /etc/nginx/sites-enabled/certbot-temp
    rm -f /etc/nginx/sites-available/certbot-temp

    # Setup auto-renewal
    cat > /etc/systemd/system/certbot-renewal.service << 'EOF'
[Unit]
Description=Certbot Renewal
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/certbot-renewal.timer << 'EOF'
[Unit]
Description=Run certbot renewal twice daily

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable certbot-renewal.timer
    systemctl start certbot-renewal.timer

    log_info "SSL certificates configured"
}

# Configure fail2ban for security
setup_fail2ban() {
    log_step "Configuring fail2ban..."

    # Create jail.local
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@rapiddocs.io
action = %(action_mwl)s

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/error.log
maxretry = 2

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
EOF

    # Create nginx filters
    cat > /etc/fail2ban/filter.d/nginx-badbots.conf << 'EOF'
[Definition]
badbots = Googlebot-Image|Googlebot|bingbot|Baiduspider|wordpress|nikto|wpscan|sqlmap
failregex = ^<HOST> .* ".*(?:%(badbots)s).*"$
ignoreregex =
EOF

    cat > /etc/fail2ban/filter.d/nginx-noproxy.conf << 'EOF'
[Definition]
failregex = ^<HOST> .* "(GET|POST|HEAD).*HTTP.*" (?:400|444) .*$
ignoreregex =
EOF

    cat > /etc/fail2ban/filter.d/nginx-limit-req.conf << 'EOF'
[Definition]
failregex = limiting requests, excess:.* by zone.*client: <HOST>
ignoreregex =
EOF

    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban

    log_info "fail2ban configured"
}

# Setup system monitoring
setup_monitoring() {
    log_step "Setting up system monitoring..."

    # Install monitoring tools
    apt install -y prometheus-node-exporter

    # Create simple monitoring script
    cat > /usr/local/bin/docgen-monitor << 'EOF'
#!/bin/bash
# Simple monitoring script

# Check disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "WARNING: Disk usage is at ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEM_USAGE" -gt 80 ]; then
    echo "WARNING: Memory usage is at ${MEM_USAGE}%"
fi

# Check if services are running
for service in nginx docgen-backend; do
    if ! systemctl is-active --quiet $service; then
        echo "ERROR: $service is not running"
        systemctl start $service
    fi
done
EOF

    chmod +x /usr/local/bin/docgen-monitor

    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/docgen-monitor >> /var/log/docgen/monitor.log 2>&1") | crontab -

    log_info "Monitoring configured"
}

# Setup backup script
setup_backups() {
    log_step "Setting up backup system..."

    # Create backup directory
    mkdir -p /backup/docgen
    chown $APP_USER:$APP_USER /backup/docgen

    # Create backup script
    cat > /usr/local/bin/docgen-backup << 'EOF'
#!/bin/bash

# Backup configuration
BACKUP_DIR="/backup/docgen"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/docgen"

# Create backup
cd $APP_DIR
tar -czf $BACKUP_DIR/docgen_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    backend/ uploads/ generated_pdfs/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "docgen_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/docgen_backup_$DATE.tar.gz"
EOF

    chmod +x /usr/local/bin/docgen-backup

    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/docgen-backup >> /var/log/docgen/backup.log 2>&1") | crontab -

    log_info "Backup system configured"
}

# Configure swap (for low memory VPS)
setup_swap() {
    log_step "Configuring swap space..."

    # Check if swap exists
    if [ $(swapon -s | wc -l) -gt 1 ]; then
        log_warn "Swap already configured"
    else
        # Create 2GB swap file
        fallocate -l 2G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile

        # Make permanent
        echo '/swapfile none swap sw 0 0' >> /etc/fstab

        # Configure swappiness
        echo 'vm.swappiness=10' >> /etc/sysctl.conf
        sysctl -p

        log_info "2GB swap configured"
    fi
}

# Setup log rotation
setup_logrotate() {
    log_step "Setting up log rotation..."

    cat > /etc/logrotate.d/docgen << 'EOF'
/var/log/docgen/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 docgen docgen
    sharedscripts
    postrotate
        systemctl reload docgen-backend >/dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
EOF

    log_info "Log rotation configured"
}

# Security hardening
security_hardening() {
    log_step "Applying security hardening..."

    # SSH hardening
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config

    # Kernel hardening
    cat >> /etc/sysctl.conf << 'EOF'

# Security hardening
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_max_syn_backlog = 2048
EOF

    sysctl -p

    # Enable automatic security updates
    dpkg-reconfigure -plow unattended-upgrades

    log_info "Security hardening applied"
}

# Final setup instructions
show_final_instructions() {
    log_step "Setup complete!"

    echo ""
    echo "=========================================="
    echo "        VPS Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Deploy your application code:"
    echo "   ./deploy.sh --host $(hostname -I | awk '{print $1}') --user root"
    echo ""
    echo "2. Update DNS records:"
    echo "   Point $DOMAIN to $(curl -s ifconfig.me)"
    echo ""
    echo "3. Configure environment variables:"
    echo "   Edit /home/docgen/backend/.env.production"
    echo ""
    echo "4. Start the service:"
    echo "   systemctl start docgen-backend"
    echo "   systemctl enable docgen-backend"
    echo ""
    echo "5. Configure Nginx site:"
    echo "   Copy nginx-production.conf to /etc/nginx/sites-available/"
    echo "   Enable the site and reload Nginx"
    echo ""
    echo "Important files:"
    echo "- Application: /home/docgen/backend/"
    echo "- Logs: /var/log/docgen/"
    echo "- Uploads: /home/docgen/uploads/"
    echo "- PDFs: /home/docgen/generated_pdfs/"
    echo "- Backups: /backup/docgen/"
    echo ""
    echo "Service commands:"
    echo "- systemctl status docgen-backend"
    echo "- journalctl -u docgen-backend -f"
    echo "- systemctl restart docgen-backend"
    echo ""
    echo "=========================================="
}

# Main execution
main() {
    log_info "Starting DocGen VPS Setup"
    log_info "This script will configure Ubuntu 22.04 for DocGen backend"

    check_root
    update_system
    install_system_packages
    setup_firewall
    create_app_user
    setup_python
    setup_mongodb_client
    setup_nginx
    setup_ssl
    setup_fail2ban
    setup_monitoring
    setup_backups
    setup_swap
    setup_logrotate
    security_hardening

    show_final_instructions
}

# Run main function
main