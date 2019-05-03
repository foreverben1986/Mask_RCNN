from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import os
import sys
import json
import numpy as np
import urllib
import time
# Root directory of the project
ROOT_DIR = os.path.abspath("../")
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from librealsense import capture
import model_load
from mrcnn import fit
from mrcnn import data_convert as dtcvt
from mrcnn import coordinates_change as cc


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
        self._set_headers()
        path,args=urllib.parse.splitquery(self.path)
#         if len(self.blackList) > 0:
#             print(self.blackList[0].decode("utf-8"))
#         self.wfile.write(bytes(str(self.blackList), "utf-8"))
        if path.find("reset") == -1:
            color_image,depth_image,depth_scale,intrinsics = capture.capture()
            print("start time: ", time.time())
            # Run detection
            results = S.model.detect([color_image], verbose=1)
            S.machine_location = dtcvt.parse_url_parameter(args)
            print("current machinelocation: ", S.machine_location)
            print("mid time: ", time.time())
            # Visualize results
            r = results[0]
            apple_data = fit.fit2(r['rois'], r['masks'],depth_image,intrinsics, depth_scale, self.blackList, S.machine_location)
            print("end time: ", time.time())
            S.currentPoint = apple_data
            if apple_data == None:
                print("there is no apple. We need to go!!!")
                self.blackList = []
                self.wfile.write(bytes("", "utf-8"))
            else:
                print("apple is at ", apple_data)
                apple_data = dtcvt.apple_data_to_str(apple_data)
                self.wfile.write(bytes(str(apple_data), "utf-8"))
        else:
            self.wfile.write(bytes("200", "utf-8"))

    def do_POST(self):
        self._set_headers()
        path,args=urllib.parse.splitquery(self.path)
        # content_len = int(self.headers.getheader('content-length', 0))
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        print("body:", post_body)
        print("args", args)
        print("currentPoint", S.currentPoint)
#         self.machine_location = dtcvt.str_to_coordinate(post_body)
        S.machine_location = dtcvt.parse_url_parameter(args)
        if path.find("black_point") != -1:
            self.blackList.append(cc.coordinateMergeZ(S.currentPoint, self.machine_location))
        self.wfile.write(bytes("200", "utf-8"))

    def do_HEAD(self):
        self._set_headers()

def run(server_class=HTTPServer,
        handler_class=S):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()
