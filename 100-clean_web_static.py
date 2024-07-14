#!/usr/bin/python3
"""
Fabric script that deletes out-of-date archives
"""
from fabric.api import env, local, run
import os
from datetime import datetime

env.hosts = ['<IP web-01>', '<IP web-02>']  # Replace with your web server IPs

def do_clean(number=0):
    """Deletes out-of-date archives"""
    try:
        number = int(number)
        if number < 1:
            number = 1
        else:
            number += 1

        # Local clean-up
        with lcd("versions"):
            local("ls -t | tail -n +{} | xargs rm -f".format(number))

        # Remote clean-up
        with cd("/data/web_static/releases"):
            run("ls -t | tail -n +{} | xargs rm -rf".format(number))

    except ValueError:
        pass
