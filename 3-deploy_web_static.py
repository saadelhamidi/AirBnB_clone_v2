#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to your web servers
"""
from fabric.api import env, put, run, local
from datetime import datetime
import os

env.hosts = ['<IP web-01>', '<IP web-02>']  # Replace with your web server IPs

def do_pack():
    """Generates a .tgz archive from the contents of the web_static folder"""
    try:
        if not os.path.exists("versions"):
            os.mkdir("versions")
        now = datetime.now()
        archive_name = "versions/web_static_{}.tgz".format(now.strftime("%Y%m%d%H%M%S"))
        local("tar -cvzf {} web_static".format(archive_name))
        return archive_name
    except:
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers"""
    if not os.path.exists(archive_path):
        return False
    
    try:
        # Extract the archive name without extension
        archive_name = os.path.basename(archive_path)
        archive_name_no_ext = archive_name.split('.')[0]

        # Define paths
        remote_tmp_path = f"/tmp/{archive_name}"
        release_dir = f"/data/web_static/releases/{archive_name_no_ext}/"

        # Upload the archive to the /tmp/ directory on the web server
        put(archive_path, remote_tmp_path)

        # Uncompress the archive to the release directory
        run(f"mkdir -p {release_dir}")
        run(f"tar -xzf {remote_tmp_path} -C {release_dir}")
        
        # Remove the archive from the web server
        run(f"rm {remote_tmp_path}")

        # Move contents out of the web_static subdirectory
        run(f"mv {release_dir}web_static/* {release_dir}")

        # Remove the empty web_static subdirectory
        run(f"rm -rf {release_dir}web_static")

        # Delete the existing symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run(f"ln -s {release_dir} /data/web_static/current")

        return True
    except:
        return False

def deploy():
    """Creates and distributes an archive to your web servers"""
    archive_path = do_pack()
    if not archive_path:
        return False
    return do_deploy(archive_path)
