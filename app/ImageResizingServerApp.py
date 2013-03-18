try:
    from PIL import Image
except ImportError:
    import Image

import httplib
import StringIO
import os
import sys
import time
import signal
import logging

import tornado.web
import tornado.wsgi
import tornado.escape
from tornado.options import define, options

define("clusterInfos", default={}, help="url of img cluster", type=dict)
define("defaultQuality", default=90, help="default output quality", type=int)
define("minHeight", default=1, help="minimum height after resize", type=int)
define("maxHeight", default=2048, help="maximum height after resize", type=int)
define("minWidth", default=1, help="minimum width after resize", type=int)
define("maxWidth", default=2048, help="maximum width after resize", type=int)
options.parse_config_file('./server.conf')

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.ERROR)

class ResizerHandler(tornado.web.RequestHandler):
    pilImage = None
    imgUrl = None
    cluster = None
    format = None
    crop = False
    quality = 90
    newHeight = 0
    newWidth = 0
    originalWidth = 0
    originalHeight = 0

    def get(self):
        self.checkParams()
        self.loadImageFromCluster()

        if self.crop:
            cropRatio = float(self.newHeight) / self.newWidth
            ratio = float(self.originalWidth) / self.originalHeight

            if cropRatio > ratio:
                cropW = self.originalWidth
                cropH = int(self.originalWidth / cropRatio) or 1
            else:
                cropH = self.originalHeight
                cropW = int(cropRatio * self.originalHeight) or 1

            cropX = int(0.5 * (self.originalWidth - cropW))
            cropY = int(0.5 * (self.originalHeight - cropH))

            self.cropImage(cropX, cropY, cropW, cropH)
            self.resizeImage()
        else:
            if self.newWidth + self.newHeight == 0:
                pass
            elif self.newWidth == self.originalWidth and self.newHeight == 0:
                pass
            elif self.newHeight == self.originalHeight and self.newWidth == 0:
                pass
            elif self.newWidth > 0 and self.newHeight == 0:
                ratio = float(self.newWidth) / self.originalWidth
                self.newHeight = int(ratio * self.originalHeight) or 1
                self.resizeImage()
            elif self.newHeight > 0 and self.newWidth == 0:
                ratio = float(self.newHeight) / self.originalHeight
                self.newWidth = int(ratio * self.originalWidth) or 1
                self.resizeImage()

        image = StringIO.StringIO()

        try:
            self.pilImage.save(image, self.format, quality=self.quality)
            self.set_header('Content-Type', 'image/' + self.format.lower())
            self.write(image.getvalue())
        except:
            msg = 'Finish Request Error {0}'.format(sys.exc_info()[ 1 ])
            LOG.error(msg)
            raise tornado.web.HTTPError(500, msg)

        return True

    def checkParams(self):
        self.imgUrl = self.get_argument('i')

        self.cluster = self.get_argument('c')
        if self.cluster not in options.clusterInfos:
            raise tornado.web.HTTPError(400, 'Bad argument c : cluster {0} not found in configuration'.format(self.cluster))

        self.crop = self.get_argument('crop', False)
        
        self.newHeight = self.get_argument('h', None)
        self.newWidth = self.get_argument('w', None)
        
        if self.crop and (self.newHeight == None or self.newWidth == None):
            raise tornado.web.HTTPError(400, 'Bad argument crop need h and w together')

        if self.newHeight != None:
            if not self.newHeight.isdigit():
                self.newHeight = 0
            
            self.newHeight = int(self.newHeight)
            if self.newHeight < options.minHeight or self.newHeight > options.maxHeight:
                raise tornado.web.HTTPError(400, 'Bad argument h : {0}>=h<{1}'.format(options.minHeight, options.maxHeight))
        else:
            self.newHeight = 0

        if self.newWidth != None:
            if not self.newWidth.isdigit():
                self.newWidth = 0
            
            self.newWidth = int(self.newWidth)
            if self.newWidth < options.minWidth or self.newWidth > options.maxWidth:
                raise tornado.web.HTTPError(400, 'Bad argument w : {0}>=w<{1}'.format(options.minWidth, options.maxWidth))
        else:
            self.newWidth = 0

        self.quality = int(self.get_argument('q', options.defaultQuality))
        if self.quality <= 0 or self.quality > 100:
            raise tornado.web.HTTPError(400, 'Bad argument q : 0>q<100')

        return True

    def loadImageFromCluster(self):
        link = httplib.HTTPConnection(
            options.clusterInfos.get(self.cluster), timeout=1)
        link.request('GET', self.imgUrl)
        resp = link.getresponse()

        status = resp.status

        if status == httplib.OK:
            content_type = resp.getheader('Content-Type')
            if content_type.startswith('image'):
                content = resp.read()
            else:
                raise tornado.web.HTTPError(415, 'Bad Content type : {0}'.format(content_type))
        else:
            msg = 'Image Not found on cluster {0}'.format(options.clusterInfos.get(self.cluster))
            LOG.error(msg)
            raise tornado.web.HTTPError(404, msg)
            
        link.close()
        content = StringIO.StringIO(content)

        try:
            self.pilImage = Image.open(content)
            self.pilImage.load()
        except:
            msg = 'Make PIL Image Error {0}'.format(sys.exc_info()[ 1 ])
            LOG.error(msg)
            raise tornado.web.HTTPError(415, msg)

        self.originalWidth, self.originalHeight = self.pilImage.size
        self.format = self.pilImage.format
        
        return True

    def resizeImage(self):
        try:
            newImg = self.pilImage.resize(
                (self.newWidth, self.newHeight), Image.ANTIALIAS)
        except:
            msg = 'Resize Error {0}'.format(sys.exc_info()[ 1 ])
            LOG.error(msg)
            raise tornado.web.HTTPError(500, msg)
        
        self.pilImage = newImg
        return True

    def cropImage(self, cropX, cropY, cropW, cropH):
        try:
            newImg = self.pilImage.crop(
                (cropX, cropY, (cropX+cropW), (cropY+cropH)))
        except:
            msg = 'Crop Error {0}'.format(sys.exc_info()[ 1 ])
            LOG.error(msg)
            raise tornado.web.HTTPError(500, msg)
        
        self.pilImage = newImg
        
    def write_error(self, status_code, **kwargs):
        if "exc_info" in kwargs:
            self.finish("<html><title>%(message)s</title>"
                    "<body>%(message)s</body></html>" % {
                    "message": tornado.escape.xhtml_escape(str(kwargs["exc_info"][1])),
                })
        else:
            self.finish("<html><title>%(code)d: %(message)s</title>"
                        "<body>%(code)d: %(message)s</body></html>" % {
                    "code": status_code,
                    "message": httplib.responses[status_code],
                    })

tornadoapp = tornado.wsgi.WSGIApplication([
    (r"/", ResizerHandler),
])

def application(environ, start_response):
    if 'SCRIPT_NAME' in environ:
        del environ['SCRIPT_NAME']
    return tornadoapp(environ, start_response)
