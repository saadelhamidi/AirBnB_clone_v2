#!/usr/bin/python3
"""
Fabric script that distributes an archive to your web servers
"""

from datetime import datetime
from fabric.api import *
import subprocess
import os
env.hosts = ["34.229.66.77", "18.209.225.222"]
env.user = "ubuntu"
env.password = "betty"


def do_pack():
    """Generate a .tgz archive from the contents of the web_static folder."""
    current_directory = os.getcwd()
    directory_path = os.path.join(current_directory, "versions")
    if not os.path.exists(directory_path):
        local("mkdir -p versions")
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    archive_name = "web_static_{}.tgz".format(timestamp)
    print(timestamp)
    archive_path = os.path.join("versions", archive_name)
    exit_status = local("tar -cvzf {} web_static/".format(archive_path))
    if exit_status.ok:
        return archive_path
    else:
        return None


def do_deploy(archive_path):
    """
        Distribute archive.
    """
    if os.path.exists(archive_path):
        name = str(archive_path).split('/')[-1]
        basename = str(name).split('.')[0]
        ver_to_deploy = "/data/web_static/releases/" + basename
        tmpname = "/tmp/" + name
        put(archive_path, "/tmp/")
        run("sudo mkdir -p {}".format(ver_to_deploy))
        run("sudo tar -xzf {} -C {}/".format(tmpname,
                                             ver_to_deploy))
        run("sudo rm {}".format(tmpname))
        run("sudo mv {}/web_static/* {}".format(ver_to_deploy,
                                                ver_to_deploy))
        run("sudo rm -rf {}/web_static/".format(ver_to_deploy))
        run("sudo rm -rf /data/web_static/current")
        run("sudo ln -s {}/ /data/web_static/current".format(ver_to_deploy))
        print("New version deployed!")
        return True

    return False


def deploy():
    """Full deployment
    """
    archive_path = do_pack()
    res = do_deploy(archive_path)
    return (res)


def do_clean(number=0):
    """  Keep it clean!
    deletes out-of-date archives,
    """

    if int(number) < 0:
        return False
    num = 1 if int(number) == 0 else int(number)
    try:
        local("ls -1t versions/ | grep '^web_static_' | tail -n +{} | \
              xargs -I {{}} rm -rf versions/{{}}".format(num + 1))
        run("ls -1t /data/web_static/releases/ | grep '^web_static_' | \
            tail -n +{} | xargs -I {{}} sudo rm -rf \
                /data/web_static/releases/{{}}".format(num + 1))
    except Exception as e:
        pass
