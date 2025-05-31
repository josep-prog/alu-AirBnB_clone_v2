#!/usr/bin/python3
"""
Backup utility for AirBnB deployment
Handles backup operations before deployment
"""

import os
import shutil
from datetime import datetime
from fabric.api import run, local
from utils.logger import log_info, log_error
from config import DEPLOYMENT_PATHS

def create_backup(server):
    """
    Create a backup of the current deployment
    
    Args:
        server (str): The server to backup
        
    Returns:
        str: Path to the backup file if successful, None otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/backup_{server}_{timestamp}.tgz"
        
        # Create backup
        log_info(f"Creating backup for {server}")
        run(f"sudo tar -czf /tmp/backup.tgz {DEPLOYMENT_PATHS['web_static']}")
        run(f"sudo chown ubuntu:ubuntu /tmp/backup.tgz")
        run(f"sudo mv /tmp/backup.tgz {backup_file}")
        
        log_info(f"Backup created successfully: {backup_file}")
        return backup_file
        
    except Exception as e:
        log_error(f"Failed to create backup for {server}", e)
        return None

def restore_backup(server, backup_file):
    """
    Restore a backup
    
    Args:
        server (str): The server to restore to
        backup_file (str): Path to the backup file
        
    Returns:
        bool: True if restore was successful, False otherwise
    """
    try:
        if not os.path.exists(backup_file):
            log_error(f"Backup file not found: {backup_file}")
            return False
            
        log_info(f"Restoring backup {backup_file} to {server}")
        
        # Stop nginx
        run("sudo service nginx stop")
        
        # Remove current deployment
        run(f"sudo rm -rf {DEPLOYMENT_PATHS['web_static']}")
        
        # Restore backup
        run(f"sudo tar -xzf {backup_file} -C /")
        
        # Fix permissions
        run(f"sudo chown -R ubuntu:ubuntu {DEPLOYMENT_PATHS['web_static']}")
        
        # Start nginx
        run("sudo service nginx start")
        
        log_info(f"Backup restored successfully to {server}")
        return True
        
    except Exception as e:
        log_error(f"Failed to restore backup to {server}", e)
        return False

def cleanup_old_backups(keep_last=5):
    """
    Clean up old backup files
    
    Args:
        keep_last (int): Number of most recent backups to keep
    """
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
            
        # Get list of backup files
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('backup_')]
        backup_files.sort(reverse=True)
        
        # Remove old backups
        for old_backup in backup_files[keep_last:]:
            backup_path = os.path.join(backup_dir, old_backup)
            os.remove(backup_path)
            log_info(f"Removed old backup: {backup_path}")
            
    except Exception as e:
        log_error("Failed to cleanup old backups", e) 