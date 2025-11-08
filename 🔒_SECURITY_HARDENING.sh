#!/bin/bash
# 🔒 SECURITY HARDENING SCRIPT
# Hardens VPS security for production trading bot deployment

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════"
echo "🔒 SECURITY HARDENING - Production VPS Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# 1. Update system
echo "1️⃣  Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
echo "   ✅ System updated"
echo ""

# 2. Install security tools
echo "2️⃣  Installing security tools..."
apt-get install -y -qq \
    ufw \
    fail2ban \
    unattended-upgrades \
    logwatch \
    rkhunter \
    aide
echo "   ✅ Security tools installed"
echo ""

# 3. Configure UFW firewall
echo "3️⃣  Configuring UFW firewall..."
ufw --force disable
ufw --force reset

# Allow SSH (change port if needed)
SSH_PORT=${SSH_PORT:-22}
ufw allow $SSH_PORT/tcp comment 'SSH'

# Allow dashboard (optional)
ufw allow 8501/tcp comment 'Streamlit Dashboard'

# Allow HTTP/HTTPS (if using nginx)
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
ufw --force enable
echo "   ✅ Firewall configured"
echo ""

# 4. Configure fail2ban
echo "4️⃣  Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = $SSH_PORT
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "   ✅ fail2ban configured"
echo ""

# 5. Configure automatic security updates
echo "5️⃣  Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

echo "   ✅ Automatic updates configured"
echo ""

# 6. Secure SSH
echo "6️⃣  Hardening SSH configuration..."
SSH_CONFIG="/etc/ssh/sshd_config"

# Backup original
cp $SSH_CONFIG ${SSH_CONFIG}.backup

# Disable root login
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' $SSH_CONFIG

# Disable password authentication (key-based only)
read -p "   Disable password auth (key-based only)? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' $SSH_CONFIG
    echo "   ⚠️  Password auth disabled - ensure SSH keys are set up!"
fi

# Other SSH hardening
sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' $SSH_CONFIG
sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' $SSH_CONFIG
sed -i 's/^#*ClientAliveInterval.*/ClientAliveInterval 300/' $SSH_CONFIG
sed -i 's/^#*ClientAliveCountMax.*/ClientAliveCountMax 2/' $SSH_CONFIG

systemctl restart sshd
echo "   ✅ SSH hardened"
echo ""

# 7. Set up IP whitelist for API access
echo "7️⃣  Setting up API IP whitelist..."
read -p "   Enter allowed IPs (comma-separated, or press Enter to skip): " ALLOWED_IPS

if [ ! -z "$ALLOWED_IPS" ]; then
    # Convert comma-separated to array
    IFS=',' read -ra IPS <<< "$ALLOWED_IPS"
    
    # Allow each IP
    for ip in "${IPS[@]}"; do
        ip=$(echo $ip | xargs)  # Trim whitespace
        ufw allow from $ip to any port 8501 comment "Dashboard - $ip"
        echo "   ✅ Allowed: $ip"
    done
    
    # Save to file for bot to use
    mkdir -p /app/config
    echo "$ALLOWED_IPS" > /app/config/allowed_ips.txt
else
    echo "   ⚠️  No IP whitelist configured (all IPs can access)"
fi
echo ""

# 8. Set up log monitoring
echo "8️⃣  Configuring log monitoring..."
cat > /etc/cron.daily/00logwatch <<EOF
#!/bin/bash
/usr/sbin/logwatch --output mail --mailto root --detail high
EOF
chmod +x /etc/cron.daily/00logwatch
echo "   ✅ Log monitoring configured"
echo ""

# 9. Kernel hardening
echo "9️⃣  Hardening kernel parameters..."
cat >> /etc/sysctl.conf <<EOF

# Security hardening
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
EOF

sysctl -p > /dev/null
echo "   ✅ Kernel hardened"
echo ""

# 10. Set up file integrity monitoring
echo "🔟 Initializing file integrity monitoring..."
aideinit
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
echo "   ✅ AIDE initialized"
echo ""

# 11. Display security status
echo "════════════════════════════════════════════════════════════"
echo "✅ SECURITY HARDENING COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Security Status:"
echo "   ✅ Firewall (UFW): Active"
ufw status numbered | head -10
echo ""
echo "   ✅ fail2ban: Active"
fail2ban-client status | head -5
echo ""
echo "   ✅ SSH: Hardened (port $SSH_PORT)"
echo "   ✅ Automatic updates: Enabled"
echo "   ✅ Log monitoring: Enabled"
echo "   ✅ File integrity: Enabled"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "   1. Save your SSH keys - password auth may be disabled"
echo "   2. Firewall is active - only allowed ports are accessible"
echo "   3. Failed login attempts will be banned (fail2ban)"
echo "   4. System will auto-update security patches"
echo "   5. Review logs daily: /var/log/auth.log"
echo ""
echo "🔐 Recommended next steps:"
echo "   1. Test SSH connection (don't close current session)"
echo "   2. Set up SSH key authentication if not already done"
echo "   3. Configure .env file with API keys"
echo "   4. Run: ./🚀_ONE_CLICK_DEPLOY.sh"
echo ""
echo "════════════════════════════════════════════════════════════"
