#!/bin/bash

# DocGen Backend Backup Script
# This script creates backups of the application data and can restore from backups

set -e  # Exit on error

# Configuration
BACKUP_DIR="/backup/docgen"
APP_DIR="/home/docgen"
REMOTE_BACKUP_HOST=""  # Optional: remote backup server
REMOTE_BACKUP_DIR=""   # Optional: remote backup directory
MONGODB_URL=""         # MongoDB connection string (from .env.production)
MAX_LOCAL_BACKUPS=7    # Keep last 7 days of local backups
MAX_REMOTE_BACKUPS=30  # Keep last 30 days of remote backups

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Timestamp for backup naming
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

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

# Load environment variables
load_env() {
    if [ -f "$APP_DIR/backend/.env.production" ]; then
        export $(grep -v '^#' "$APP_DIR/backend/.env.production" | xargs)
        MONGODB_URL="${MONGODB_URL:-$MONGODB_URL}"
    else
        log_warn "Environment file not found. MongoDB backup will be skipped."
    fi
}

# Create backup directory structure
create_backup_dirs() {
    mkdir -p "$BACKUP_DIR/daily"
    mkdir -p "$BACKUP_DIR/weekly"
    mkdir -p "$BACKUP_DIR/monthly"
    mkdir -p "$BACKUP_DIR/temp"
}

# Backup application files
backup_files() {
    log_info "Backing up application files..."

    local backup_name="docgen_files_${TIMESTAMP}.tar.gz"
    local temp_backup="$BACKUP_DIR/temp/$backup_name"

    # Create tarball of application files
    tar -czf "$temp_backup" \
        -C "$APP_DIR" \
        --exclude='backend/venv' \
        --exclude='backend/__pycache__' \
        --exclude='backend/*.pyc' \
        --exclude='backend/*.log' \
        --exclude='backend/.git' \
        backend/ \
        uploads/ \
        generated_pdfs/

    # Move to daily backups
    mv "$temp_backup" "$BACKUP_DIR/daily/"

    log_info "Files backed up to: $BACKUP_DIR/daily/$backup_name"

    echo "$backup_name"
}

# Backup MongoDB database
backup_mongodb() {
    if [ -z "$MONGODB_URL" ]; then
        log_warn "MongoDB URL not configured. Skipping database backup."
        return
    fi

    log_info "Backing up MongoDB database..."

    local backup_name="docgen_mongodb_${TIMESTAMP}"
    local temp_backup="$BACKUP_DIR/temp/$backup_name"

    # Create MongoDB dump
    mongodump \
        --uri="$MONGODB_URL" \
        --out="$temp_backup" \
        --quiet

    # Compress the dump
    tar -czf "${temp_backup}.tar.gz" -C "$BACKUP_DIR/temp" "$backup_name"
    rm -rf "$temp_backup"

    # Move to daily backups
    mv "${temp_backup}.tar.gz" "$BACKUP_DIR/daily/"

    log_info "MongoDB backed up to: $BACKUP_DIR/daily/${backup_name}.tar.gz"

    echo "${backup_name}.tar.gz"
}

# Backup environment configuration
backup_config() {
    log_info "Backing up configuration files..."

    local backup_name="docgen_config_${TIMESTAMP}.tar.gz"
    local temp_backup="$BACKUP_DIR/temp/$backup_name"

    # Create tarball of config files
    tar -czf "$temp_backup" \
        -C "$APP_DIR/backend" \
        .env.production \
        gunicorn_production.conf.py \
        requirements-production.txt \
        2>/dev/null || true

    # Add nginx config if exists
    if [ -f "/etc/nginx/sites-available/docgen-api" ]; then
        tar -rzf "$temp_backup" \
            -C /etc/nginx/sites-available \
            docgen-api \
            2>/dev/null || true
    fi

    # Add systemd service if exists
    if [ -f "/etc/systemd/system/docgen-backend.service" ]; then
        tar -rzf "$temp_backup" \
            -C /etc/systemd/system \
            docgen-backend.service \
            2>/dev/null || true
    fi

    # Move to daily backups
    mv "$temp_backup" "$BACKUP_DIR/daily/"

    log_info "Configuration backed up to: $BACKUP_DIR/daily/$backup_name"

    echo "$backup_name"
}

# Rotate backups (daily -> weekly -> monthly)
rotate_backups() {
    log_info "Rotating backups..."

    # Get day of week and day of month
    DOW=$(date +%w)  # 0 = Sunday
    DOM=$(date +%d)

    # Weekly backup on Sunday
    if [ "$DOW" -eq 0 ]; then
        log_info "Creating weekly backup..."
        cp "$BACKUP_DIR/daily/"*"${TIMESTAMP}"* "$BACKUP_DIR/weekly/" 2>/dev/null || true
    fi

    # Monthly backup on 1st day of month
    if [ "$DOM" -eq 1 ]; then
        log_info "Creating monthly backup..."
        cp "$BACKUP_DIR/daily/"*"${TIMESTAMP}"* "$BACKUP_DIR/monthly/" 2>/dev/null || true
    fi

    # Clean old backups
    clean_old_backups
}

# Clean old backups
clean_old_backups() {
    log_info "Cleaning old backups..."

    # Clean daily backups older than MAX_LOCAL_BACKUPS days
    find "$BACKUP_DIR/daily" -name "docgen_*.tar.gz" -mtime +$MAX_LOCAL_BACKUPS -delete

    # Clean weekly backups older than 4 weeks
    find "$BACKUP_DIR/weekly" -name "docgen_*.tar.gz" -mtime +28 -delete

    # Clean monthly backups older than 6 months
    find "$BACKUP_DIR/monthly" -name "docgen_*.tar.gz" -mtime +180 -delete

    log_info "Old backups cleaned"
}

# Upload backup to remote server
upload_to_remote() {
    local backup_file=$1

    if [ -z "$REMOTE_BACKUP_HOST" ] || [ -z "$REMOTE_BACKUP_DIR" ]; then
        log_info "Remote backup not configured. Skipping remote upload."
        return
    fi

    log_info "Uploading backup to remote server..."

    # Use rsync for efficient transfer
    rsync -avz \
        "$BACKUP_DIR/daily/$backup_file" \
        "${REMOTE_BACKUP_HOST}:${REMOTE_BACKUP_DIR}/"

    if [ $? -eq 0 ]; then
        log_info "Backup uploaded to remote server successfully"

        # Clean old remote backups
        ssh "$REMOTE_BACKUP_HOST" \
            "find $REMOTE_BACKUP_DIR -name 'docgen_*.tar.gz' -mtime +$MAX_REMOTE_BACKUPS -delete"
    else
        log_error "Failed to upload backup to remote server"
    fi
}

# Restore from backup
restore_backup() {
    local backup_type=$1
    local backup_date=$2

    log_warn "Starting restore process..."
    log_warn "This will overwrite current data! Press Ctrl+C to cancel."
    sleep 5

    # Find backup files
    local file_backup=$(ls -t "$BACKUP_DIR/daily/docgen_files_${backup_date}"*.tar.gz 2>/dev/null | head -1)
    local db_backup=$(ls -t "$BACKUP_DIR/daily/docgen_mongodb_${backup_date}"*.tar.gz 2>/dev/null | head -1)
    local config_backup=$(ls -t "$BACKUP_DIR/daily/docgen_config_${backup_date}"*.tar.gz 2>/dev/null | head -1)

    if [ -z "$file_backup" ]; then
        log_error "No file backup found for date: $backup_date"
        exit 1
    fi

    # Stop services
    log_info "Stopping services..."
    sudo systemctl stop docgen-backend

    # Restore files
    if [ -n "$file_backup" ]; then
        log_info "Restoring files from: $file_backup"
        tar -xzf "$file_backup" -C "$APP_DIR"
    fi

    # Restore MongoDB
    if [ -n "$db_backup" ] && [ -n "$MONGODB_URL" ]; then
        log_info "Restoring MongoDB from: $db_backup"
        temp_dir=$(mktemp -d)
        tar -xzf "$db_backup" -C "$temp_dir"
        mongorestore --uri="$MONGODB_URL" --dir="$temp_dir" --drop
        rm -rf "$temp_dir"
    fi

    # Restore configuration
    if [ -n "$config_backup" ]; then
        log_info "Restoring configuration from: $config_backup"
        tar -xzf "$config_backup" -C /
    fi

    # Restart services
    log_info "Restarting services..."
    sudo systemctl start docgen-backend

    log_info "Restore completed successfully"
}

# List available backups
list_backups() {
    echo "Available backups:"
    echo ""
    echo "Daily backups:"
    ls -lh "$BACKUP_DIR/daily/" | grep docgen_files

    echo ""
    echo "Weekly backups:"
    ls -lh "$BACKUP_DIR/weekly/" | grep docgen_files

    echo ""
    echo "Monthly backups:"
    ls -lh "$BACKUP_DIR/monthly/" | grep docgen_files
}

# Show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  backup    - Create a new backup"
    echo "  restore   - Restore from backup"
    echo "  list      - List available backups"
    echo "  clean     - Clean old backups"
    echo ""
    echo "Options:"
    echo "  --remote  - Also upload to remote server"
    echo "  --date    - Backup date for restore (YYYYMMDD format)"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 backup --remote"
    echo "  $0 restore --date 20240121"
    echo "  $0 list"
}

# Main execution
main() {
    case ${1:-} in
        backup)
            load_env
            create_backup_dirs

            # Perform backups
            files_backup=$(backup_files)
            db_backup=$(backup_mongodb)
            config_backup=$(backup_config)

            # Rotate backups
            rotate_backups

            # Upload to remote if requested
            if [[ "${2:-}" == "--remote" ]]; then
                upload_to_remote "$files_backup"
                upload_to_remote "$db_backup"
                upload_to_remote "$config_backup"
            fi

            log_info "Backup completed successfully"
            ;;

        restore)
            if [[ "${2:-}" != "--date" ]] || [ -z "${3:-}" ]; then
                log_error "Please specify date: $0 restore --date YYYYMMDD"
                exit 1
            fi
            load_env
            restore_backup "daily" "$3"
            ;;

        list)
            list_backups
            ;;

        clean)
            clean_old_backups
            ;;

        *)
            show_usage
            ;;
    esac
}

# Run main function
main "$@"