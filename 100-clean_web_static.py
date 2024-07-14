#!/usr/bin/python3
"""
Fabric script to distribute an archive to web servers.
"""

from datetime import datetime
from fabric.api import *
import subprocess
import os

# Define the target hosts and user credentials
env.hosts = ["34.229.66.77", "18.209.225.222"]
env.user = "ubuntu"
env.password = "betty"

def do_pack():
    """Create a .tgz archive from the web_static folder."""
    current_directory = os.getcwd()
    versions_directory = os.path.join(current_directory, "versions")
    
    # Create versions directory if it doesn't exist
    if not os.path.exists(versions_directory):
        local("mkdir -p versions")
    
    # Generate archive name with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    archive_name = f"web_static_{timestamp}.tgz"
    archive_path = os.path.join("versions", archive_name)
    
    # Create the archive
    result = local(f"tar -cvzf {archive_path} web_static/")
    return archive_path if result.ok else None

def do_deploy(archive_path):
    """Deploy the archive to the web servers."""
    if os.path.exists(archive_path):
        file_name = os.path.basename(archive_path)
        base_name = os.path.splitext(file_name)[0]
        release_dir = f"/data/web_static/releases/{base_name}"
        tmp_path = f"/tmp/{file_name}"
        
        # Transfer and extract the archive
        put(archive_path, tmp_path)
        run(f"sudo mkdir -p {release_dir}")
        run(f"sudo tar -xzf {tmp_path} -C {release_dir}")
        run(f"sudo rm {tmp_path}")
        run(f"sudo mv {release_dir}/web_static/* {release_dir}")
        run(f"sudo rm -rf {release_dir}/web_static")
        
        # Update the current symlink
        run("sudo rm -rf /data/web_static/current")
        run(f"sudo ln -s {release_dir} /data/web_static/current")
        
        print("New version deployed!")
        return True
    
    return False

def deploy():
    """Execute the full deployment process."""
    archive_path = do_pack()
    if archive_path:
        return do_deploy(archive_path)
    return False

def do_clean(number=0):
    """Remove outdated archives."""
    number = max(1, int(number))
    
    # Clean local archives
    local(f"ls -1t versions/ | grep '^web_static_' | tail -n +{number + 1} | xargs -I {{}} rm -rf versions/{{}}")
    
    # Clean remote archives
    run(f"ls -1t /data/web_static/releases/ | grep '^web_static_' | tail -n +{number + 1} | xargs -I {{}} sudo rm -rf /data/web_static/releases/{{}}")
