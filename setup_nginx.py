#!/usr/bin/python3
"""
Setup Nginx configuration for serving static files
"""

from fabric.api import env, run, sudo

# Server configurations
env.hosts = ['52.71.25.46', '54.86.41.67']  # web-01 and web-02
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'

def setup_nginx():
    """Setup Nginx configuration for serving static files"""
    try:
        # Create Nginx configuration
        nginx_config = """
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location /hbnb_static {
        alias /data/web_static/current/;
        index index.html;
        try_files $uri $uri/ =404;
    }
}
"""
        # Write configuration to temporary file
        run('echo "{}" > /tmp/nginx_config'.format(nginx_config))
        
        # Backup current configuration
        run('sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak')
        
        # Update configuration
        run('sudo mv /tmp/nginx_config /etc/nginx/sites-available/default')
        
        # Test configuration
        if run('sudo nginx -t').failed:
            print("Nginx configuration test failed")
            run('sudo mv /etc/nginx/sites-available/default.bak /etc/nginx/sites-available/default')
            return False
            
        # Restart Nginx
        run('sudo service nginx restart')
        
        print("Nginx configuration updated successfully")
        return True
        
    except Exception as e:
        print(f"Failed to setup Nginx: {str(e)}")
        return False 