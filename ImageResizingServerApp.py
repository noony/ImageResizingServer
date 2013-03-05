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
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("muninEnabled", default=True, help="have munin stats", type=bool)
define("clusterInfos", default={}, help="url of img cluster", type=dict)

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
            LOG.error('Finish Request Error {0}'.format(sys.exc_info()[ 1 ]))
            self.send_error(500)

        return True

    def checkParams(self):
        self.imgUrl = self.get_argument('i')

        self.cluster = self.get_argument('c')
        if self.cluster not in options.clusterInfos:
            self.send_error(400)

        self.crop = self.get_argument('crop', False)

        if self.crop:
            self.newHeight = self.get_argument('h')
            self.newWidth = self.get_argument('w')
        else:
            self.newHeight = self.get_argument('h', None)
            self.newWidth = self.get_argument('w', None)

        if self.newHeight != None:
            self.newHeight = int(self.newHeight)
            if self.newHeight < 1 or self.newHeight > 2048:
                self.send_error(400)
        else:
            self.newHeight = 0

        if self.newWidth != None:
            self.newWidth = int(self.newWidth)
            if self.newWidth < 1 or self.newWidth > 2048:
                self.send_error(400)
        else:
            self.newWidth = 0

        self.quality = int(self.get_argument('q', 90))
        if self.quality < 0 or self.quality > 100:
            self.send_error(400)

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
                self.send_error(415)
        else:
            self.send_error(404)
            
        link.close()
        content = StringIO.StringIO(content)

        try:
            self.pilImage = Image.open(content)
            self.pilImage.load()
            self.originalWidth, self.originalHeight = self.pilImage.size
            self.format = self.pilImage.format
        except:
            LOG.error('Make PIL Image Error {0}'.format(sys.exc_info()[ 1 ]))
            self.send_error(415)

        return True

    def resizeImage(self):
        try:
            newImg = self.pilImage.resize(
                (self.newWidth, self.newHeight), Image.ANTIALIAS)
            self.pilImage = newImg
        except:
            LOG.error('Resize Error {0}'.format(sys.exc_info()[ 1 ]))
            self.send_error(500)
        return True

    def cropImage(self, cropX, cropY, cropW, cropH):
        try:
            newImg = self.pilImage.crop(
                (cropX, cropY, (cropX+cropW), (cropY+cropH)))
            self.pilImage = newImg
        except:
            LOG.error('Crop Error {0}'.format(sys.exc_info()[ 1 ]))
            self.send_error(500)

tornadoapp = tornado.wsgi.WSGIApplication([
    (r"/", ResizerHandler),
])

def application(environ, start_response):
    if 'SCRIPT_NAME' in environ:
        del environ['SCRIPT_NAME']
    return tornadoapp(environ, start_response)
