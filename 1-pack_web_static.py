#!/usr/bin/python3
"""
Fabric script that generates a .tgz archive from the contents of the web_static folder
"""
from fabric.api import local
from datetime import datetime
import os

def do_pack():
    """Generates a .tgz archive from the contents of the web_static folder"""
    dt_string = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_name = f"web_static_{dt_string}.tgz"
    versions_dir = "versions"

    # Create versions directory if it doesn't exist
    if not os.path.exists(versions_dir):
        os.makedirs(versions_dir)

    # Create the archive
    archive_path = os.path.join(versions_dir, archive_name)
    cmd = f"tar -cvzf {archive_path} web_static"

    result = local(cmd)

    if result.failed:
        return None
    return archive_path
