#!/bin/bash

# Log Management Script
# Organizes and cleans up old log files

LOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/logs"
ARCHIVE_DIR="$LOG_DIR/archive"
DAYS_TO_KEEP=7

echo "=========================================="
echo "Log Management Script"
echo "=========================================="

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$ARCHIVE_DIR"

# Count files before cleanup
total_files=$(find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" | wc -l)
echo "Total log files: $total_files"

# Find and archive old logs
old_logs=$(find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -mtime +$DAYS_TO_KEEP)

if [ -z "$old_logs" ]; then
    echo "No old logs to archive"
else
    echo "Archiving logs older than $DAYS_TO_KEEP days..."
    
    for log in $old_logs; do
        filename=$(basename "$log")
        gzip -c "$log" > "$ARCHIVE_DIR/${filename}.gz"
        rm "$log"
        echo "  - Archived: $filename"
    done
fi

# Clean up archives older than 30 days
echo ""
echo "Cleaning archives older than 30 days..."
find "$ARCHIVE_DIR" -type f -name "*.log.gz" -mtime +30 -delete
echo "Old archives cleaned"

# Display current status
echo ""
echo "Current Status:"
echo "  Active logs: $(find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" | wc -l)"
echo "  Archived logs: $(find "$ARCHIVE_DIR" -type f -name "*.log.gz" | wc -l)"
echo "  Disk usage: $(du -sh "$LOG_DIR" | cut -f1)"

echo ""
echo "Log management completed!"
echo "=========================================="
