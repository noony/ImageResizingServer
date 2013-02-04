ImageResizerServer
==================

This server allows you to resize and manipulate images. It uses tornado, uwsgi and nginx.

Installation & Configuration
-----------

	pip install tornado uwsgi
	apt-get install python-imaging nginx

	cd /tmp
	git clone https://github.com/noony/ImageResizerServer.git
	cd ./ImageResizerServer

	mkdir /srv/ImageResizerServer
	cp ./ImageResizerServer.py /srv/ImageResizerServer
	cp ./config.ini /srv/ImageResizerServer

	cp ./nginx-conf/ImageResizerServer /etc/nginx/site-enabled/
	/etc/init.d/nginx/ restart
    
run standalone
	uwsgi --ini /srv/ImageResizerServer/config.ini


