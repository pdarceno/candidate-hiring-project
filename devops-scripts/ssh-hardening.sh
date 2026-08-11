#!/bin/bash

# SSH Hardening Script
# Secures SSH configuration on production servers

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "SSH Security Hardening Script"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Usage: sudo ./ssh-hardening.sh"
    exit 1
fi

SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP_FILE="${SSHD_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

# Backup current configuration
echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"
cp "$SSHD_CONFIG" "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup created${NC}"
echo ""

# Function to update SSH config
update_ssh_config() {
    local setting=$1
    local value=$2
    
    if grep -q "^#*${setting}" "$SSHD_CONFIG"; then
        sed -i "s/^#*${setting}.*/${setting} ${value}/" "$SSHD_CONFIG"
    else
        echo "${setting} ${value}" >> "$SSHD_CONFIG"
    fi
}

echo "Applying security hardening..."

# 1. Disable root login
echo "  - Disabling root login"
update_ssh_config "PermitRootLogin" "no"

# 2. Disable password authentication (use keys only)
echo "  - Disabling password authentication"
update_ssh_config "PasswordAuthentication" "no"
update_ssh_config "ChallengeResponseAuthentication" "no"

# 3. Enable public key authentication
echo "  - Enabling public key authentication"
update_ssh_config "PubkeyAuthentication" "yes"

# 4. Disable empty passwords
echo "  - Disabling empty passwords"
update_ssh_config "PermitEmptyPasswords" "no"

# 5. Set maximum authentication attempts
echo "  - Setting max auth tries to 3"
update_ssh_config "MaxAuthTries" "3"

# 6. Set login grace time
echo "  - Setting login grace time to 20 seconds"
update_ssh_config "LoginGraceTime" "20"

# 7. Disable X11 forwarding (if not needed)
echo "  - Disabling X11 forwarding"
update_ssh_config "X11Forwarding" "no"

# 8. Set maximum sessions
echo "  - Setting max sessions to 3"
update_ssh_config "MaxSessions" "3"

# 9. Use strong ciphers only
echo "  - Configuring strong ciphers"
update_ssh_config "Ciphers" "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr"

# 10. Use strong MACs
echo "  - Configuring strong MACs"
update_ssh_config "MACs" "hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256"

# 11. Set client alive interval (prevents timeout)
echo "  - Setting client alive interval"
update_ssh_config "ClientAliveInterval" "300"
update_ssh_config "ClientAliveCountMax" "2"

echo ""
echo -e "${GREEN}✓ Security hardening applied${NC}"
echo ""

# Validate configuration
echo "Validating SSH configuration..."
if sshd -t; then
    echo -e "${GREEN}✓ Configuration is valid${NC}"
    echo ""
    
    # Ask for restart confirmation
    echo -e "${YELLOW}SSH service needs to be restarted for changes to take effect.${NC}"
    echo "Current SSH connections will NOT be dropped."
    echo ""
    read -p "Restart SSH service now? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl restart sshd
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ SSH service restarted successfully${NC}"
        else
            echo -e "${RED}✗ Failed to restart SSH service${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Restart skipped. Run: systemctl restart sshd${NC}"
    fi
else
    echo -e "${RED}✗ Configuration validation failed!${NC}"
    echo "Restoring backup..."
    cp "$BACKUP_FILE" "$SSHD_CONFIG"
    echo -e "${GREEN}✓ Backup restored${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "SSH Hardening Summary"
echo "=========================================="
echo "✓ Root login disabled"
echo "✓ Password authentication disabled"
echo "✓ Public key authentication enabled"
echo "✓ Strong ciphers configured"
echo "✓ Connection limits set"
echo ""
echo "Backup saved: $BACKUP_FILE"
echo ""
echo -e "${GREEN}SSH security hardening completed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Ensure your SSH key is added to authorized_keys"
echo "2. Test SSH connection in a NEW terminal (don't close this one)"
echo "3. Consider installing fail2ban: apt install fail2ban"
echo "4. Consider changing SSH port (update Port in $SSHD_CONFIG)"
echo ""
