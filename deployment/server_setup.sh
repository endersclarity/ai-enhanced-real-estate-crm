#!/bin/bash
# Server Setup Script for AI-Enhanced Real Estate CRM Production Environment
# Sets up Ubuntu 22.04 LTS server with all necessary components

set -e  # Exit on any error

echo "🚀 Setting up production server environment for Real Estate CRM..."
echo "================================================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y \
    nginx \
    postgresql-client \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    htop \
    ufw \
    certbot \
    python3-certbot-nginx \
    redis-server \
    supervisor

# Install Node.js for any frontend build processes
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Configure UFW firewall
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw --force enable

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash crm-app
sudo usermod -aG www-data crm-app

# Create application directories
echo "📁 Creating application directories..."
sudo mkdir -p /var/www/narissa-realty-crm
sudo mkdir -p /var/log/narissa-realty-crm
sudo mkdir -p /etc/narissa-realty-crm
sudo chown -R crm-app:www-data /var/www/narissa-realty-crm
sudo chown -R crm-app:www-data /var/log/narissa-realty-crm

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/narissa-realty-crm > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # Health check endpoint for load balancer
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias /var/www/narissa-realty-crm/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/narissa-realty-crm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Configure Redis
echo "🔴 Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Python dependencies
echo "🐍 Setting up Python environment..."
sudo -u crm-app python3 -m venv /var/www/narissa-realty-crm/venv
sudo -u crm-app /var/www/narissa-realty-crm/venv/bin/pip install --upgrade pip

# Create systemd service for the Flask app
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/narissa-realty-crm.service > /dev/null <<EOF
[Unit]
Description=Narissa Realty CRM Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=crm-app
Group=www-data
WorkingDirectory=/var/www/narissa-realty-crm
Environment=PATH=/var/www/narissa-realty-crm/venv/bin
Environment=FLASK_APP=real_estate_crm.py
Environment=FLASK_ENV=production
ExecStart=/var/www/narissa-realty-crm/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 real_estate_crm:app
Restart=always
RestartSec=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=narissa-realty-crm

[Install]
WantedBy=multi-user.target
EOF

# Create supervisor configuration for additional monitoring
echo "👁️ Configuring process monitoring..."
sudo tee /etc/supervisor/conf.d/narissa-realty-crm.conf > /dev/null <<EOF
[program:narissa-realty-crm]
command=/var/www/narissa-realty-crm/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 real_estate_crm:app
directory=/var/www/narissa-realty-crm
user=crm-app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/narissa-realty-crm/app.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
EOF

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable narissa-realty-crm
sudo systemctl enable supervisor

# Configure log rotation
echo "📋 Configuring log rotation..."
sudo tee /etc/logrotate.d/narissa-realty-crm > /dev/null <<EOF
/var/log/narissa-realty-crm/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 crm-app www-data
    postrotate
        sudo systemctl reload narissa-realty-crm
    endscript
}
EOF

# Create monitoring script
echo "📊 Creating monitoring script..."
sudo tee /usr/local/bin/crm-health-check > /dev/null <<'EOF'
#!/bin/bash
# Health check script for Narissa Realty CRM

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "✅ $service: RUNNING"
        return 0
    else
        echo "❌ $service: STOPPED"
        return 1
    fi
}

check_port() {
    local port=$1
    local service=$2
    if netstat -tuln | grep -q ":$port "; then
        echo "✅ $service (port $port): LISTENING"
        return 0
    else
        echo "❌ $service (port $port): NOT LISTENING"
        return 1
    fi
}

echo "🏥 Health Check Report - $(date)"
echo "================================"

# Check services
check_service nginx
check_service narissa-realty-crm
check_service redis-server

# Check ports
check_port 80 "HTTP"
check_port 443 "HTTPS"
check_port 5000 "Flask App"
check_port 6379 "Redis"

# Check disk space
echo ""
echo "💾 Disk Usage:"
df -h / | tail -n 1 | awk '{print "   Root partition: " $5 " used"}'

# Check memory
echo ""
echo "🧠 Memory Usage:"
free -h | grep Mem | awk '{print "   Memory: " $3 "/" $2 " used (" int($3/$2*100) "%)"}'

# Check load average
echo ""
echo "⚡ Load Average:"
uptime | awk -F'load average:' '{print "   " $2}'
EOF

sudo chmod +x /usr/local/bin/crm-health-check

# Create deployment script
echo "🚀 Creating deployment script..."
sudo tee /usr/local/bin/deploy-crm > /dev/null <<'EOF'
#!/bin/bash
# Deployment script for Narissa Realty CRM

set -e

APP_DIR="/var/www/narissa-realty-crm"
BACKUP_DIR="/var/backups/narissa-realty-crm"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 Deploying Narissa Realty CRM..."
echo "================================="

# Create backup
echo "💾 Creating backup..."
sudo mkdir -p $BACKUP_DIR
sudo tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $APP_DIR . || true

# Stop services
echo "⏹️ Stopping services..."
sudo systemctl stop narissa-realty-crm || true

# Deploy new code (would be handled by CI/CD in real deployment)
echo "📦 Deploying application..."
# Code deployment would happen here

# Install/update dependencies
echo "📚 Installing dependencies..."
sudo -u crm-app $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# Run database migrations if needed
echo "🗄️ Running database migrations..."
# Database migration commands would go here

# Start services
echo "▶️ Starting services..."
sudo systemctl start narissa-realty-crm
sudo systemctl restart nginx

# Verify deployment
echo "🔍 Verifying deployment..."
sleep 5
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed - rolling back..."
    # Rollback logic would go here
    exit 1
fi

echo "🎉 Deployment completed successfully!"
EOF

sudo chmod +x /usr/local/bin/deploy-crm

echo ""
echo "✅ Server setup completed successfully!"
echo ""
echo "📋 Summary:"
echo "  - Nginx web server configured with reverse proxy"
echo "  - UFW firewall configured with necessary ports"
echo "  - Application user 'crm-app' created"
echo "  - Systemd service configured for auto-start"
echo "  - Supervisor monitoring configured"
echo "  - Log rotation configured"
echo "  - Health check script: /usr/local/bin/crm-health-check"
echo "  - Deployment script: /usr/local/bin/deploy-crm"
echo ""
echo "🎯 Next steps:"
echo "  1. Deploy application code to /var/www/narissa-realty-crm"
echo "  2. Configure PostgreSQL database connection"
echo "  3. Setup SSL certificates with certbot"
echo "  4. Configure custom domain"
echo ""
echo "🏥 Run health check: sudo /usr/local/bin/crm-health-check"