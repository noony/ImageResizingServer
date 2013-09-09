Image Resizing Server
==================

This server provides a service to resize and crop images with a simple API. It's able to hold heavy loads and is easy to use.

It was written in Python, using Tornado web framework, Uwsgi to distribute the application on the network and Nginx front-end.

I want to specially thanks Stéphane Bunel (https://bitbucket.org/StephaneBunel), he was the initiator of this project, and advised me on how to re-develop this project for open-sourcing.

It's my first open-source project, feel free to contribute.

Installation
-----------

need sudo :
```bash
apt-get install python-pip python-imaging nginx build-essential python-dev libxml2-dev && pip install uwsgi tornado
cd /tmp && git clone https://github.com/noony/ImageResizingServer.git && cd ./ImageResizingServer
python setup.py install
```
Attention if you haven't installed nginx you have to remove default conf in sites-enabled (rm /etc/nginx/sites-enabled/default)

Configuration
-----------

You have to define your image clusters. It a simple dict in server.conf

default :

    clusterInfos = {
    }
    signatureSecret = ""
    timeoutGetCluster = 1
    defaultQuality = 90
    minHeight = 1
    maxHeight = 2048
    minWidth = 1
    maxWidth = 2048


Example : 

    clusterInfos = {
        'cluster1': 'url.cluster1.com',
        'cluster2': 'url.cluster2.com'
    }
    signatureSecret = "MY_SECRET_TOKEN"
    timeoutGetCluster = 1
    defaultQuality = 100
    minHeight = 1
    maxHeight = 1024
    minWidth = 1
    maxWidth = 1024

You have to restart uwsgi after.

Examples
-----------
Resize an image to 100px width :

http://example.com/cluster1/100x0/path/to/image.png

Resize an image to 300px height :

http://example.com/cluster1/0x300/path/to/image.png

Resize an image to 600px width and change is quality to 60% :

http://example.com/cluster1/60/600x0/path/to/image.png

Crop an image and resize 200/200px :

http://example.com/cluster1/crop/200x200/path/to/image.png

Crop an image and resize 200/200px and change quality to 95% :

http://example.com/cluster1/crop/95/200x200/path/to/image.png

Securise your application
-----------
If you want to securise the application, put a token in configuration directive "signatureSecret".

And after to retrieve the signature you just have to follow this example:

configuration: signatureSecret="YOUR_SECRET_TOKEN"

uri: /cluster1/crop/95/200x200/path/to/image.png

Python :
```python
import hashlib
hashlib.sha512('YOUR_SECRET_TOKEN' + '/cluster1/crop/95/200x200/path/to/image.png').hexdigest()[:4]
result : '61b5'
```
PHP :
```php
substr(hash('sha512', 'YOUR_SECRET_TOKEN' . '/cluster1/crop/95/200x200/path/to/image.png'), 0, 4);
result : '61b5'
```

Final uri : /61b5//cluster1/crop/95/200x200/path/to/image.png
