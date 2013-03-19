ImageResizingServer
==================

This server provides a service to resize and crop images with a simple GET API. It's able to hold heavy loads and is easy to use.

It was written in Python, using Tornado web framework, Uwsgi to distribute the application on the network and Nginx front-end.

I want to specially thanks Stéphane Bunel, he was the initiator of this project, and advised me on how to re-develop this project for open-sourcing.

Installation
-----------

    cd /tmp && git clone https://github.com/noony/ImageResizingServer.git
    cd ./ImageResizingServer

    mkdir /var/www/ImageResizingServer
    cp app/* /var/www/ImageResizingServer/

need sudo :

    apt-get install python-pip python-imaging uwsgi nginx build-essential python-dev libxml2-dev
    pip install tornado
    
    cp ./ImageResizingServer.ini /etc/uwsgi/apps-enabled/
    /etc/init.d/uwsgi restart
    
    cp ./nginx-conf/ImageResizingServer /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/ImageResizingServer /etc/nginx/sites-enabled/ImageResizingServer 
    /etc/init.d/nginx restart

Configuration
-----------

You have to define your image clusters. It a simple dict in server.conf

Example : 

    clusterInfos = {
        '1': 'url.cluster1.com',
        '2': 'url.cluster2.com'
    }

You have to restart uwsgi after.

Examples
-----------
Resize an image to 100px width :

http://example.com/?c=1&=/path/to/image.png&w=100

Resize an image to 300px height :

http://example.com/?c=1&=/path/to/image.png&h=300

Resize an image to 600px width and change is quality to 60% :

http://example.com/?c=1&=/path/to/image.png&w=600&q=60

Crop an image and resize 200/200px :

http://example.com/?c=1&=/path/to/image.png&w=200&h=200&crop=1

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

q= desired quality, default 90, ex: 100

* **crop**

crop= if you want to crop image set this parameter. Crop need both parameter h and w. Crop take the larger box with your resize ratio and resize to the specified size.
