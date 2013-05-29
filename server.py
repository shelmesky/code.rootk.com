#coding: utf-8
#!/usr/bin/evn python
import os
import sys
import copy
import functools
import base64
import httplib2
import urllib
import simplejson as json
import socket

import tornado.ioloop
from tornado.web import RequestHandler
from tornado.httpserver import HTTPServer
from tornado.web import StaticFileHandler
from tornado.web import asynchronous
from tornado import httpclient
from tornado import httputil

USERNAME = "tornado"
PASSWORD = "storm"
TAOBAO_IP_API = "http://ip.taobao.com/service/getIpInfo.php?ip="

class ipTOAddress(object):
    def make_request(self, url, method, body=None):
        headers = httputil.HTTPHeaders()
        headers.add('Accept', 'application/json')
        request = httpclient.HTTPRequest(
            url = url,
            method = method,
            connect_timeout = 3
        )
        return request
    
    def request(self, uri, callback, method="GET", **kwargs):
        request = self.make_request(uri, method, **kwargs)
        client = httpclient.AsyncHTTPClient()
        client.fetch(request, callback)
    
    def __call__(self, ip, callback=None):
        self.request(TAOBAO_IP_API+ip, callback)
    

def authenticated(auth):
    def decore(f):
        def _request_auth(handler):
            handler.set_header('WWW-Authenticate', 'Basic realm=code.rootk.com')
            handler.set_status(401)
            handler.write("<p>Authorization Failed</p><p>If you want username and password, please contact roy@rootk.com</p>")
            return False

        @functools.wraps(f)
        def new_f(handler, *args, **kwargs):
            auth_header = handler.request.headers.get('Authorization')
            if auth_header is None: 
                return _request_auth(handler)
            if not auth_header.startswith('Basic '): 
                return _request_auth(handler)
    
            auth_decoded = base64.decodestring(auth_header[6:])
            username, password = auth_decoded.split(':', 2)
    
            if (auth(username, password)):
                f(handler, *args, **kwargs)
            else:
                _request_auth(handler)
        return new_f
    return decore


def count(f):
    @functools.wraps(f)
    def wrapper(handler, *args, **kwargs):
        return f(handler, *args, **kwargs)
    return wrapper


def login(username, password):
    if username == USERNAME and password == PASSWORD:
        return True
    else:
        return False


class Main(RequestHandler):
    @authenticated(login)
    @asynchronous
    def get(self):
        ip_remote = self.request.remote_ip
        ipCheck = ipTOAddress()
        ip_detail = ipCheck(ip_remote, callback=self.on_callback)
    
    def on_callback(self, response):
        body = json.loads(response.body)
        self.render("index.html", ip_info=body)
        return
    

class Entry(RequestHandler):
    @authenticated(login)
    @count
    def get(self, entry):
        self.render(entry + "/index.html")
        return


if __name__ == '__main__':
    settings = {
        "cookie_secret": "27yc1u%9tt3$o^$3uu=6e(=2d7mykjd8@dc*#x0z%vm&0_vdq",
        "debug": True,   # debug mode not compatible with multiprocessing environment.
        "gzip": True,
        'static_path': os.path.join(os.path.dirname(__file__), "static")
    }
    
    
    app = tornado.web.Application([
        (r"/", Main),
        (r"/entry/([^/]+)", Entry),
        (r"/static/.*", StaticFileHandler, dict(path=settings['static_path'])),
        ], **settings)


    if settings.get('debug', None) == False:
        server = HTTPServer(app, xheaders=True)
        server.bind(8000, family=socket.AF_INET)
        server.start(4)
    else:
        server = HTTPServer(app, xheaders=True)
        server.bind(8000, family=socket.AF_INET)
        server.start()
    
    tornado.ioloop.IOLoop.instance().start()

