ImageResizingServer
==================

This server providing a service to resize image with a simple API in GET. It's able to hold heavy loads and is easy to use.

It was written in Python, using Tornado web framework, Uwsgi to distribute the application on the network and Nginx front-end.

Installation & Configuration
-----------

    cd /tmp && git clone https://github.com/noony/ImageResizingServer.git
    cd ./ImageResizingServer

    mkdir /var/www/ImageResizingServer
    cp ImageResizingServer.py /var/www/ImageResizingServer/

need sudo :

    apt-get install python-pip python-imaging uwsgi nginx build-essential python-dev libxml2-dev
    pip install tornado
    
    cp ./ImageResizingServer.ini /etc/uwsgi/apps-enabled/
    /etc/init.d/uwsgi restart
    
    cp ./nginx-conf/ImageResizingServer /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/ImageResizingServer /etc/nginx/sites-enabled/ImageResizingServer 
    /etc/init.d/nginx restart

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

* **q**

quality= desired quality, default 90, ex: 100

