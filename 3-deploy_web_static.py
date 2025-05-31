#!/usr/bin/python3
"""
Fabric script to create and distribute an archive to web servers
"""

from fabric.api import env, local, put, run
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
    """Deploy web_static to web servers"""
    if not exists(archive_path):
        return False
        
    try:
        # Get archive filename without extension
        archive_name = archive_path.split('/')[-1]
        archive_name_no_ext = archive_name.split('.')[0]
        
        # Upload archive to /tmp/
        put(archive_path, '/tmp/')
        
        # Create release directory
        run(f'mkdir -p /data/web_static/releases/{archive_name_no_ext}/')
        
        # Uncompress archive
        run(f'tar -xzf /tmp/{archive_name} -C /data/web_static/releases/{archive_name_no_ext}/')
        
        # Remove archive from /tmp/
        run(f'rm /tmp/{archive_name}')
        
        # Move contents to release directory
        run(f'mv /data/web_static/releases/{archive_name_no_ext}/web_static/* '
            f'/data/web_static/releases/{archive_name_no_ext}/')
        
        # Remove empty web_static directory
        run(f'rm -rf /data/web_static/releases/{archive_name_no_ext}/web_static')
        
        # Remove current symlink
        run('rm -rf /data/web_static/current')
        
        # Create new symlink
        run(f'ln -s /data/web_static/releases/{archive_name_no_ext}/ '
            '/data/web_static/current')
        
        # Ensure proper permissions
        run('chmod -R 755 /data/web_static/')
        
        print("New version deployed!")
        return True
        
    except Exception as e:
        return False

def deploy():
    """Create and distribute an archive to web servers"""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

