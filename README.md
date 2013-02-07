ImageResizingServer
==================

This server providing a service to resize image with a simple API in GET. It is able to hold heavy loads and is easy to use.

It was written in Python, using the Tornado framework, using Uwsgi to distribute the application on the network and of course there is Nginx front-end.

Installation & Configuration
-----------

need sudo :

    apt-get install python-pip python-imaging nginx build-essential python-dev libxml2-dev
    pip install tornado uwsgi


    cd /srv && git clone https://github.com/noony/ImageResizingServer.git
    cd ./ImageResizingServer

    cp ./nginx-conf/ImageResizingServer /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/ImageResizingServer /etc/nginx/sites-enabled/ImageResizingServer 
    /etc/init.d/nginx restart
    
    cp ./init-script/ImageResizingServer /etc/init.d/.
    chmod 0755 /etc/init.d/ImageResizingServer

Run
-----
As service

    /etc/init.d/ImageResizingServer start

Standalone

    uwsgi --ini /srv/ImageResizingServer/config.ini


API
-----------

* **i**

i=  Image path, ex : /path/to/image.png

* **c**

c=  Cluster where is stocked original image, ex: cluster1

* **w**

w= desired width, max 2048, ex: 760

* **h**

h= desired height, max 2048, ex: 110

