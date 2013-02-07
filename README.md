ImageResizerServer
==================

This server providing a service to resize image with a simple API in GET. It is able to hold heavy loads and is easy to use.

It was written in Python, using the Tornado framework, using Uwsgi to distribute the application on the network and of course there is Nginx front-end.

Installation & Configuration
-----------

    cd /srv && git clone https://github.com/noony/ImageResizerServer.git
    cd ./ImageResizerServer
    
need sudo :

    pip install tornado uwsgi
    apt-get install python-imaging nginx

    cp ./nginx-conf/ImageResizerServer /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/ImageResizerServer /etc/nginx/sites-enabled/ImageResizerServer 
    /etc/init.d/nginx/ restart
    
    cp ./init-script/ImageResizerServer /etc/init.d/.
    chmod 0755 /etc/init.d/ImageResizerServer

Run
-----
As service

    /etc/init.d/ImageResizerServer start

Standalone

    uwsgi --ini /srv/ImageResizerServer/config.ini


API
-----------

* **i**

i=  Image path, ex : /path/to/image.png

* **c**

c=  Cluster where is stocked original image, ex: cluster1

* **w**

h= desired width, max 2048, ex: 760

* **h**

h= desired height, max 2048, ex: 110

