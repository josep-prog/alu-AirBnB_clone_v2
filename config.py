#!/usr/bin/python3
"""
Configuration file for AirBnB deployment
Contains all configurable parameters for deployment
"""

# Server configurations
WEB_SERVERS = {
    'web-01': {
        'host': '52.71.25.46',
        'user': 'ubuntu',
        'key_file': '~/.ssh/id_rsa'
    },
    'web-02': {
        'host': '54.86.41.67',
        'user': 'ubuntu',
        'key_file': '~/.ssh/id_rsa'
    },
    'lb-01': {
        'host': '54.235.237.101',
        'user': 'ubuntu',
        'key_file': '~/.ssh/id_rsa'
    }
}

# Deployment paths
DEPLOYMENT_PATHS = {
    'web_static': '/data/web_static',
    'releases': '/data/web_static/releases',
    'shared': '/data/web_static/shared',
    'current': '/data/web_static/current'
}

# Nginx configuration
NGINX_CONFIG = {
    'config_path': '/etc/nginx/sites-enabled/default',
    'static_location': '/hbnb_static',
    'max_upload_size': '10M',
    'keepalive_timeout': '65',
    'client_max_body_size': '10M'
}

# Deployment settings
DEPLOYMENT = {
    'keep_releases': 5,  # Number of releases to keep
    'backup_before_deploy': True,
    'health_check_timeout': 30,  # seconds
    'health_check_path': '/hbnb_static/0-index.html'
}

# Logging configuration
LOGGING = {
    'log_file': '/var/log/airbnb_deploy.log',
    'max_size': '10M',
    'backup_count': 5
}

# Security settings
SECURITY = {
    'ssl_enabled': False,
    'rate_limit': '100r/s',
    'allowed_ips': []  # List of IPs allowed to access admin endpoints
} 