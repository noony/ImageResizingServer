#!/usr/bin/env python

import distutils.core
import sys

try:
    import setuptools
except ImportError:
    pass

kwargs = {}

distutils.core.setup(
    name="ImageResizingServer",
    version=version,
    data_files= [
        ('/etc/nginx/sites-enabled/', ['./nginx-conf/ImageResizingServer']),
        ('/etc/uwsgi/apps-enabled/', ['./uwsgi-conf/ImageResizingServerApp.ini']),
        ('/srv/ImageResizingServer', ['./app/server.conf', './app/ImageResizingServerApp.py'])
    ],
    author="Thomas Colomb",
    author_email="",
    url="https://github.com/noony",
    download_url="https://github.com/noony/ImageResizingServer/tarball/master",
    license="",
    description="This server provides a service to resize and crop images with a simple API.",
    classifiers=[
        ],
    **kwargs
)
