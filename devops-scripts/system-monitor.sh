#!/bin/bash

# System Resource Monitor Script
# Monitors CPU, Memory, Disk, and Docker container resources

echo "=========================================="
echo "System Resource Monitor"
echo "Timestamp: $(date)"
echo "=========================================="
echo ""

# CPU Usage
echo "=== CPU Usage ==="
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU Usage: " 100 - $1"%"}'
echo ""

# Memory Usage
echo "=== Memory Usage ==="
free -h | awk '/^Mem:/ {printf "Total: %s | Used: %s | Free: %s | Usage: %.2f%%\n", $2, $3, $4, ($3/$2)*100}'
echo ""

# Disk Usage
echo "=== Disk Usage ==="
df -h / | awk 'NR==2 {printf "Total: %s | Used: %s | Available: %s | Usage: %s\n", $2, $3, $4, $5}'
echo ""

# Docker Container Stats
echo "=== Docker Container Resources ==="
if command -v docker &> /dev/null; then
    if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    else
        echo "No running Docker containers"
    fi
else
    echo "Docker not installed"
fi
echo ""

# Running Processes (top 10 by CPU)
echo "=== Top 10 Processes by CPU ==="
ps aux --sort=-%cpu | head -11 | awk '{printf "%-10s %-8s %-6s %-6s %s\n", $1, $2, $3, $4, $11}'
echo ""

# Network Connections
echo "=== Active Network Connections ==="
netstat -tuln | grep LISTEN | wc -l | awk '{print "Listening ports: " $1}'
echo ""

echo "=========================================="
echo "Monitor completed at $(date)"
echo "=========================================="
