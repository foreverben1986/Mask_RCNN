from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import os
import sys
import json
import numpy as np
import urllib
import time
import logging
import logging.config
# Root directory of the project
ROOT_DIR = os.path.abspath("../")
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from librealsense import capture
import model_load
from mrcnn import fit
from mrcnn import data_convert as dtcvt
from mrcnn import coordinates_change as cc


logging.config.fileConfig(os.path.join(ROOT_DIR, 'logging/logging.conf'))
# create logger
logger = logging.getLogger('shlxLog')

class S(BaseHTTPRequestHandler):
    blackList = []
    currentPoint = (0,0,0)
    machine_location = (0,0,0)
    model = model_load.load_model()
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.debug("+++++++++++++++++++++++++++++++++++++++++++++")
        self._set_headers()
        path,args=urllib.parse.splitquery(self.path)
#         if len(self.blackList) > 0:
#             print(self.blackList[0].decode("utf-8"))
#         self.wfile.write(bytes(str(self.blackList), "utf-8"))
        if path.find("reset") == -1:
            color_image,depth_image,depth_scale,intrinsics, file_name = capture.capture(True)
#             color_image,depth_image,depth_scale,intrinsics, file_name = capture.capture()
            # Run detection
            results = S.model.detect([color_image], verbose=1)
            logger.debug("args %s: ", args)
            S.machine_location = dtcvt.parse_url_parameter(args)
            logger.debug("start process %s: ", file_name)
            logger.debug("current machinelocation: %s", S.machine_location)
            # Visualize results
            r = results[0]
            apple_data = fit.fit2(r['rois'], r['masks'],depth_image,intrinsics, depth_scale, self.blackList, S.machine_location)
            S.currentPoint = apple_data
            if apple_data == None:
                logger.debug("There is no apple. We need to go.")
                self.blackList = []
                self.wfile.write(bytes("", "utf-8"))
            else:
                logger.debug("apple is at %s: ", apple_data)
                apple_data = dtcvt.apple_data_to_str(apple_data)
                self.wfile.write(bytes(str(apple_data), "utf-8"))
            logger.debug("end process %s: ", file_name)
        else:
            S.blackList=[]
            self.wfile.write(bytes("200", "utf-8"))
        logging.debug("+++++++++++++++++++++++++++++++++++++++++++++")

    def do_POST(self):
        logging.debug("----------------------------------------------")
        self._set_headers()
        path,args=urllib.parse.splitquery(self.path)
        # content_len = int(self.headers.getheader('content-length', 0))
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
#         self.machine_location = dtcvt.str_to_coordinate(post_body)
        S.machine_location = dtcvt.parse_url_parameter(args)
        logger.debug("currentPoint %s: ", S.currentPoint)
        logger.debug("machine_location %s: ", S.machine_location)
        if path.find("black_point") != -1:
            self.blackList.append(cc.coordinateMergeZ(S.currentPoint, S.machine_location))
        self.wfile.write(bytes("200", "utf-8"))
        logging.debug("----------------------------------------------")

    def do_HEAD(self):
        self._set_headers()

def run(server_class=HTTPServer,
        handler_class=S):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()
