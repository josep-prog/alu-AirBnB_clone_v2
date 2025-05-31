#!/usr/bin/python3
"""
Improved deployment script for AirBnB
Handles deployment with proper error handling, logging, and rollback
"""

from fabric.api import env, local, put, run, sudo
from datetime import datetime
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WEB_SERVERS, DEPLOYMENT_PATHS, DEPLOYMENT
from utils.logger import log_info, log_error, log_deployment_start, log_deployment_end
from utils.health_check import check_server_health, wait_for_healthy
from utils.backup import create_backup, restore_backup, cleanup_old_backups
from utils.nginx_config import update_nginx_config, setup_ssl
from utils.monitoring import setup_monitoring

# Set Fabric environment
env.hosts = [server['host'] for server in WEB_SERVERS.values()]
env.user = WEB_SERVERS['web-01']['user']  # Use same user for all servers
env.key_filename = WEB_SERVERS['web-01']['key_file']

def setup_server(server_name):
    """Setup a server with all required components"""
    try:
        # Update Nginx configuration
        if not update_nginx_config():
            log_error(f"Failed to update Nginx configuration on {server_name}")
            return False
            
        # Setup SSL if enabled
        if not setup_ssl():
            log_error(f"Failed to setup SSL on {server_name}")
            return False
            
        # Setup monitoring
        if not setup_monitoring():
            log_error(f"Failed to setup monitoring on {server_name}")
            return False
            
        return True
        
    except Exception as e:
        log_error(f"Failed to setup server {server_name}", e)
        return False

def do_pack():
    """Generate a .tgz archive from web_static folder"""
    try:
        # Create versions directory if it doesn't exist
        if not os.path.exists("versions"):
            local("mkdir versions")
            
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_path = f"versions/web_static_{timestamp}.tgz"
        
        # Create archive
        log_info(f"Creating archive: {archive_path}")
        local(f"tar -cvzf {archive_path} web_static")
        
        if os.path.exists(archive_path):
            log_info(f"Archive created successfully: {archive_path}")
            return archive_path
        else:
            log_error("Archive creation failed")
            return None
            
    except Exception as e:
        log_error("Failed to create archive", e)
        return None

def do_deploy(archive_path):
    """Deploy archive to web servers"""
    if not os.path.exists(archive_path):
        log_error(f"Archive not found: {archive_path}")
        return False
        
    # Get archive filename without extension
    archive_name = os.path.basename(archive_path)
    archive_name_no_ext = os.path.splitext(archive_name)[0]
    
    # Deploy to each server
    for server_name, server_config in WEB_SERVERS.items():
        if server_name == 'lb-01':  # Skip load balancer
            continue
            
        log_deployment_start(server_name, archive_name)
        
        try:
            # Create backup if enabled
            if DEPLOYMENT['backup_before_deploy']:
                backup_file = create_backup(server_name)
                if not backup_file:
                    log_error(f"Backup failed for {server_name}")
                    return False
            
            # Upload archive
            put(archive_path, '/tmp/')
            
            # Create release directory
            release_path = f"{DEPLOYMENT_PATHS['releases']}/{archive_name_no_ext}"
            run(f"sudo mkdir -p {release_path}")
            
            # Uncompress archive
            run(f"sudo tar -xzf /tmp/{archive_name} -C {release_path}")
            
            # Remove archive
            run(f"sudo rm /tmp/{archive_name}")
            
            # Move contents
            run(f"sudo mv {release_path}/web_static/* {release_path}/")
            run(f"sudo rm -rf {release_path}/web_static")
            
            # Update symbolic link
            run(f"sudo rm -rf {DEPLOYMENT_PATHS['current']}")
            run(f"sudo ln -s {release_path} {DEPLOYMENT_PATHS['current']}")
            
            # Fix permissions
            run(f"sudo chown -R ubuntu:ubuntu {DEPLOYMENT_PATHS['web_static']}")
            
            # Setup server components
            if not setup_server(server_name):
                log_error(f"Failed to setup server components on {server_name}")
                if DEPLOYMENT['backup_before_deploy'] and backup_file:
                    log_info(f"Attempting to restore backup for {server_name}")
                    restore_backup(server_name, backup_file)
                return False
            
            # Wait for server to be healthy
            if not wait_for_healthy(f"http://{server_config['host']}"):
                log_error(f"Server {server_name} failed health check after deployment")
                if DEPLOYMENT['backup_before_deploy'] and backup_file:
                    log_info(f"Attempting to restore backup for {server_name}")
                    restore_backup(server_name, backup_file)
                return False
                
            log_deployment_end(server_name, archive_name, True)
            
        except Exception as e:
            log_error(f"Deployment failed for {server_name}", e)
            if DEPLOYMENT['backup_before_deploy'] and backup_file:
                log_info(f"Attempting to restore backup for {server_name}")
                restore_backup(server_name, backup_file)
            log_deployment_end(server_name, archive_name, False)
            return False
            
    # Cleanup old backups
    cleanup_old_backups(DEPLOYMENT['keep_releases'])
    
    return True

def deploy():
    """Full deployment process"""
    # Create archive
    archive_path = do_pack()
    if not archive_path:
        log_error("Archive creation failed")
        return False
        
    # Deploy archive
    return do_deploy(archive_path) 