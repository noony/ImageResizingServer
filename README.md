ImageResizingServer
==================

This server providing a service to resize image with a simple API in GET. It's able to hold heavy loads and is easy to use.

It was written in Python, using Tornado web framework, Uwsgi to distribute the application on the network and Nginx front-end.

I want to specially thanks Stéphane Bunel, he was the initiator of this project, and advised me on how to re-develop this project for open-sourcing.

Installation
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

Configuration
-----------

You have to define your image clusters. It a simple dict in ImageResizingServerApp.py

Example : 

    define("clusterInfos", default={'1': 'url.cluster1.com', '2': 'url.cluster2.com'}, help="url of img cluster", type=dict)

You have to restart uwsgi after.

Examples
-----------
Resize an image to 100px width :

http://example.com/?c=1&=/path/to/image.png&w=100

Resize an image to 300px height :

http://example.com/?c=1&=/path/to/image.png&h=300

Resize an image to 600px width and change is quality to 60% :

http://example.com/?c=1&=/path/to/image.png&w=600&q=60

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

