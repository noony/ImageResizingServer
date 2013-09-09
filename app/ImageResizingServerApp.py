try:
    from PIL import Image
except ImportError:
    import Image

import os
import re
import sys
import time
import signal
import logging
import httplib
import hashlib
import StringIO

import tornado.web
import tornado.wsgi
import tornado.escape
from tornado.options import define, options

define("clusterInfos", default={}, help="url of img cluster", type=dict)
define(
    "signatureSecret", default="", help="add signature to request", type=str)
define("defaultQuality", default=90, help="default output quality", type=int)
define("minHeight", default=1, help="minimum height after resize", type=int)
define("maxHeight", default=2048, help="maximum height after resize", type=int)
define("minWidth", default=1, help="minimum width after resize", type=int)
define("maxWidth", default=2048, help="maximum width after resize", type=int)
define("timeoutGetCluster", default=1,
       help="timeout for get image on cluster", type=int)
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

    def get(self, signature, cluster, crop, quality, width, height, imgUrl):
        self.checkParams(
            signature, cluster, crop, quality, width, height, imgUrl)
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
            else:
                self.resizeImage()

        image = StringIO.StringIO()

        try:
            self.pilImage.save(image, self.format, quality=self.quality)
            self.set_header('Content-Type', 'image/' + self.format.lower())
            self.write(image.getvalue())
        except:
            msg = 'Finish Request Error {0}'.format(sys.exc_info()[1])
            LOG.error(msg)
            raise tornado.web.HTTPError(500, msg)

    def checkParams(self, signature, cluster, crop, quality, width, height, imgUrl):
        self.imgUrl = '/' + imgUrl
        self.newHeight = int(height)
        self.newWidth = int(width)
        self.cluster = cluster

        if options.signatureSecret is not "" and (signature is None or signature[:4] != hashlib.sha512(options.signatureSecret + self.request.uri[5:]).hexdigest()[:4]):
            raise tornado.web.HTTPError(403, 'Bad signature')

        if self.cluster not in options.clusterInfos:
            raise tornado.web.HTTPError(
                400, 'Bad argument Cluster : cluster {0} not found in configuration'.format(self.cluster))

        if self.newHeight == 0 and self.newWidth == 0:
            raise tornado.web.HTTPError(
                400, 'Bad argument Height and Width can\'t be both at 0')

        if self.newHeight != 0:
            if self.newHeight < options.minHeight or self.newHeight > options.maxHeight:
                raise tornado.web.HTTPError(
                    400, 'Bad argument Height : {0}>=h<{1}'.format(options.minHeight, options.maxHeight))

        if self.newWidth != 0:
            if self.newWidth < options.minWidth or self.newWidth > options.maxWidth:
                raise tornado.web.HTTPError(
                    400, 'Bad argument Width : {0}>=w<{1}'.format(options.minWidth, options.maxWidth))

        if quality is not None:
            self.quality = int(re.match(r'\d+', quality).group())
        else:
            self.quality = options.defaultQuality

        if self.quality <= 0 or self.quality > 100:
            raise tornado.web.HTTPError(400, 'Bad argument Quality : 0>q<100')

        if crop is not None:
            self.crop = True
            if self.newWidth == 0 or self.newHeight == 0:
                raise tornado.web.HTTPError(
                    400, 'Crop error, you have to sprecify both Width ({0}) and Height ({1})'.format(self.newWidth, self.newHeight))

        return True

    def loadImageFromCluster(self):
        link = httplib.HTTPConnection(
            options.clusterInfos.get(self.cluster), timeout=options.timeoutGetCluster)
        link.request('GET', self.imgUrl)
        resp = link.getresponse()

        status = resp.status

        if status == httplib.OK:
            content_type = resp.getheader('Content-Type')
            if content_type.startswith('image'):
                content = resp.read()
            else:
                raise tornado.web.HTTPError(
                    415, 'Bad Content type : {0}'.format(content_type))
        else:
            msg = 'Image not found on cluster {0}'.format(self.cluster)
            LOG.error(msg)
            raise tornado.web.HTTPError(404, msg)

        link.close()
        content = StringIO.StringIO(content)

        try:
            self.pilImage = Image.open(content)
            self.pilImage.load()
        except:
            msg = 'Make PIL Image Error {0}'.format(sys.exc_info()[1])
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
            msg = 'Resize Error {0}'.format(sys.exc_info()[1])
            LOG.error(msg)
            raise tornado.web.HTTPError(500, msg)

        self.pilImage = newImg
        return True

    def cropImage(self, cropX, cropY, cropW, cropH):
        try:
            newImg = self.pilImage.crop(
                (cropX, cropY, (cropX + cropW), (cropY + cropH)))
        except:
            msg = 'Crop Error {0}'.format(sys.exc_info()[1])
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
    (r"/([0-9a-zA-Z]{4}/)?([0-9a-zA-Z]+)/(crop/)?(\d+/)?(\d+)x(\d+)/(.+)",
     ResizerHandler),
])


def application(environ, start_response):
    if 'SCRIPT_NAME' in environ:
        del environ['SCRIPT_NAME']
    return tornadoapp(environ, start_response)
