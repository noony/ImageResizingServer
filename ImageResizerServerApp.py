from PIL import Image

import httplib
import StringIO
import os
import sys
import time
import signal

import tornado.web
import tornado.wsgi
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("muninEnabled", default=True, help="have munin stats", type=bool)
define("clusterInfos", default={}, help="url of img cluster", type=dict)

class ResizerHandler(tornado.web.RequestHandler):
    pilImage = None
    imgUrl = None
    cluster = None
    format = None
    new_height = 0
    new_width = 0
    original_width = 0
    original_height = 0
    
    def get(self):
        self.checkParams()
        self.loadImageFromCluster()
        
        if self.new_width + self.new_height == 0:
            pass
        elif self.new_width == self.original_width and self.new_height == 0:
            pass
        elif self.new_height == self.original_height and self.new_width == 0:
            pass
        elif self.new_width > 0 and self.new_height == 0:
            ratio = float(self.new_width) / self.original_width
            self.new_height = int(ratio * self.original_height) or 1
            self.resizeImage()
        elif self.new_height > 0 and self.new_width == 0:
            ratio = float(self.new_height) / self.original_height
            self.new_width = int(ratio * self.original_width) or 1
            self.resizeImage()
        
        image = StringIO.StringIO()
        format = 'jpeg'
        
        try:
            self.pilImage.save(image, format)#, quality=context[ 'param_q' ])
            self.set_header('Content-Type', 'image/' + format.lower())
            self.write(image.getvalue())
            self.finish()
        except:
            print sys.exc_info()[1]
            self.send_error(500)

        return True
    
    def checkParams(self):
        self.imgUrl = self.get_argument('i')
        
        self.cluster = self.get_argument('c')
        if self.cluster not in options.clusterInfos:
            self.send_error(400)
        
        self.new_height = self.get_argument('h', None)
        self.new_width = self.get_argument('w', None)
        
        if self.new_height != None:
            self.new_height = int(self.new_height)
            if self.new_height < 1 or self.new_height > 2048:
                self.send_error(400)
        else:
            self.new_height = 0
                
        if self.new_width != None:
            self.new_width = int(self.new_width)
            if self.new_width < 1 or self.new_width > 2048:
                self.send_error(400)
        else:
            self.new_width = 0
        
        return True
    
    def loadImageFromCluster(self):
        if self.cluster == 'local':
            content = os.path.abspath(self.cluster + self.imgUrl)
            if content.startswith(self.cluster):
                self.send_error(404)
            
        else:
            link = httplib.HTTPConnection( options.clusterInfos.get(self.cluster), timeout = 1 )
            link.request( 'GET', self.imgUrl )
            resp = link.getresponse()

            status = resp.status
            
            if status == httplib.OK:
                content_type = resp.getheader( 'Content-Type' )
                if content_type.startswith( 'image' ):
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
            self.original_width, self.original_height = self.pilImage.size
            self.format = self.pilImage.format
        except:
            print sys.exc_info()[1]
            self.send_error(415)
        
        return True

    def resizeImage(self):
        start_time = time.time()
        try:
            test = self.pilImage.resize((self.new_width, self.new_height), Image.ANTIALIAS)
            self.pilImage = test
        except:
            self.send_error(500)
        print 'Resize : ' + str( ( time.time() - start_time ) * 1000.0 )
        return True

tornadoapp = tornado.wsgi.WSGIApplication([
    (r"/", ResizerHandler),
])
 
def application(environ, start_response):
    if 'SCRIPT_NAME' in environ:
        del environ['SCRIPT_NAME']
    return tornadoapp(environ, start_response)
 
