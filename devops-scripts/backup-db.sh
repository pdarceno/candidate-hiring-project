#!/bin/bash

# Database Backup Script
# Creates timestamped backups of PostgreSQL database

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/candidate_db_$TIMESTAMP.sql"
DAYS_TO_KEEP=14

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Database Backup Script"
echo "=========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get database container name
DB_CONTAINER=$(docker compose ps -q db)

if [ -z "$DB_CONTAINER" ]; then
    echo "Error: Database container not running"
    exit 1
fi

# Perform backup
echo "Creating backup..."
docker compose exec -T db pg_dump -U postgres postgres > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created: ${BACKUP_FILE}.gz${NC}"
    
    # Show backup size
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo "  Size: $SIZE"
else
    echo "Error: Backup failed"
    exit 1
fi

# Clean old backups
echo ""
echo "Cleaning backups older than $DAYS_TO_KEEP days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$DAYS_TO_KEEP -delete

# Show backup status
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo ""
echo "Backup Status:"
echo "  Total backups: $BACKUP_COUNT"
echo "  Total size: $TOTAL_SIZE"
echo ""
echo -e "${GREEN}Backup completed successfully!${NC}"
echo "=========================================="
