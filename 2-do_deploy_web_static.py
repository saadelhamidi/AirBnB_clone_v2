#!/usr/bin/python3
"""
Fabric script that distributes an archive to your web servers
"""

from datetime import datetime
from fabric import Connection, task
import os

env.hosts = ["34.229.66.77", "18.209.225.222"]
env.user = "ubuntu"
env.password = "betty"


@task
def do_deploy(c, archive_path):
    """
    Distribute archive.
    """
    if os.path.exists(archive_path):
        archive_name = os.path.basename(archive_path)
        archive_basename = os.path.splitext(archive_name)[0]
        remote_path = "/data/web_static/releases/"

        # Upload archive to /tmp/ on the server
        c.put(archive_path, "/tmp/")

        # Create necessary directories
        c.sudo(f"mkdir -p {remote_path}{archive_basename}")

        # Extract archive
        c.sudo(f"tar -xzf /tmp/{archive_name} -C {remote_path}{archive_basename}/")

        # Remove archive from /tmp/
        c.sudo(f"rm /tmp/{archive_name}")

        # Move contents to proper location
        c.sudo(f"mv {remote_path}{archive_basename}/web_static/* {remote_path}{archive_basename}/")

        # Remove redundant web_static directory
        c.sudo(f"rm -rf {remote_path}{archive_basename}/web_static/")

        # Update symbolic link
        c.sudo(f"rm -rf /data/web_static/current")
        c.sudo(f"ln -s {remote_path}{archive_basename}/ /data/web_static/current")

        # Configure Nginx
        nginx_config = """
        server {
            listen 80 default_server;
            listen [::]:80 default_server;

            root /data/web_static/releases/{};
            index index.html;

            location /redirect_me {{
                return 301 http://localhost/new_page;
            }}

            error_page 404 /404.html;
            location = /404.html {{
                internal;
            }}

            location /hbnb_static/ {{
                alias /data/web_static/current/;
            }}

            location / {{
                add_header X-Served-By "$(hostname)";
            }}
        }}
        """.format(archive_basename)

        # Write and reload Nginx configuration
        c.sudo(f"echo '{nginx_config}' | tee /etc/nginx/sites-available/default")
        c.sudo("service nginx reload")

        print("New version deployed!")
        return True

    return False
