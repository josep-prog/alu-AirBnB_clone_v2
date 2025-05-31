#!/usr/bin/python3
"""
Fabric script to create and distribute an archive to web servers
"""

from fabric.api import env, local, put, run, sudo
from datetime import datetime
from os.path import exists, isdir

# Server configurations
env.hosts = ['52.71.25.46', '54.86.41.67']  # web-01 and web-02
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'

def do_pack():
    """Create a tar gzipped archive of the web_static directory"""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            local("mkdir -p versions")
        file_name = f"versions/web_static_{date}.tgz"
        local(f"tar -cvzf {file_name} web_static")
        return file_name
    except Exception:
        return None

def do_deploy(archive_path):
    """Deploy web_static to web servers
    
    Args:
        archive_path: Path to the archive file
        
    Returns:
        True if deployment is successful, False otherwise
    """
    if not exists(archive_path):
        return False
        
    try:
        # Get archive filename without extension
        archive_name = archive_path.split('/')[-1]
        archive_name_no_ext = archive_name.split('.')[0]
        
        # Upload archive to /tmp/
        put(archive_path, '/tmp/')
        
        # Create release directory
        run(f'sudo mkdir -p /data/web_static/releases/{archive_name_no_ext}/')
        
        # Uncompress archive
        run(f'sudo tar -xzf /tmp/{archive_name} -C /data/web_static/releases/{archive_name_no_ext}/')
        
        # Remove archive from /tmp/
        run(f'sudo rm /tmp/{archive_name}')
        
        # Move contents to release directory
        run(f'sudo mv /data/web_static/releases/{archive_name_no_ext}/web_static/* '
            f'/data/web_static/releases/{archive_name_no_ext}/')
        
        # Remove empty web_static directory
        run(f'sudo rm -rf /data/web_static/releases/{archive_name_no_ext}/web_static')
        
        # Remove current symlink
        run('sudo rm -rf /data/web_static/current')
        
        # Create new symlink
        run(f'sudo ln -s /data/web_static/releases/{archive_name_no_ext}/ '
            '/data/web_static/current')
        
        # Set proper permissions
        run('sudo chown -R ubuntu:ubuntu /data/web_static/')
        run('sudo chmod -R 755 /data/web_static/')
        
        # Ensure Nginx configuration
        nginx_config = """
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /data/web_static/current;
    index index.html index.htm;
    server_name _;
    location /hbnb_static {
        alias /data/web_static/current;
        try_files $uri $uri/ =404;
    }
}
"""
        run('echo "{}" | sudo tee /etc/nginx/sites-available/default'.format(nginx_config))
        
        # Restart Nginx to ensure changes take effect
        run('sudo service nginx restart')
        
        print("New version deployed!")
        return True
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        return False

def deploy():
    """Create and distribute an archive to web servers"""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

