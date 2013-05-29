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
import argparse

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
            # 是有启用HTTP Basic AUTH方式认证
            if handler.settings['user_auth']:
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
            else:
                f(handler, *args, **kwargs)
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
        if self.settings['ip2address']:
            ip_remote = self.request.remote_ip
            ipCheck = ipTOAddress()
            ip_detail = ipCheck(ip_remote, callback=self.on_callback)
        else:
            #由于在国外VPS上调用TAOBAO IP地址库API容易导致超时
            #所以在此禁用
            self.on_callback(None)
    
    def on_callback(self, response):
        body = json.loads(response.body) if response else None
        self.render("index.html", ip_info=body)
        return
    

class Entry(RequestHandler):
    @authenticated(login)
    @count
    def get(self, entry):
        self.render(entry + "/index.html")
        return


#make current process goto daemon
def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir(".") 
    os.umask(0) 
    os.setsid() 

    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Now I am a daemon!
    
    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="code.rootk.com")
    exclusive_group = parser.add_mutually_exclusive_group(required=False)
    exclusive_group.add_argument('-r', '--dryrun', action='store_true',
                            dest='dryrun', default=False, help='just do dry run')
    exclusive_group.add_argument('-d', '--daemon', action='store_true',
                            dest='daemon', default=False, help='make this process go background.')
    
    sysargs = sys.argv[1:]
    args = parser.parse_args(args=sysargs)
    if len(sysargs) < 1:
        parser.print_help()
        sys.exit(1)
    else:
        if args.dryrun:
           pass
        elif args.daemon:
           print "we will disappear from console :)"
           daemonize()
    
    settings = {
        "cookie_secret": "27yc1u%9tt3$o^$3uu=6e(=2d7mykjd8@dc*#x0z%vm&0_vdq",
        "debug": True,   # debug mode not compatible with multiprocessing environment.
        "gzip": True,
        'static_path': os.path.join(os.path.dirname(__file__), "static"),
        'ip2address': False,    # 获得客户端的IP地址，并查询TAOBAO IP地址库得到物理地址
        'user_auth': False      # 使用HTTP BASIC AUTH认证
    }
    
    
    app = tornado.web.Application([
        (r"/", Main),
        (r"/entry/([^/]+)", Entry),
        (r"/static/.*", StaticFileHandler, dict(path=settings['static_path'])),
        ], **settings)


    server = HTTPServer(app, xheaders=True)
    server.bind(8000, family=socket.AF_INET)
    
    if settings.get('debug', None) == False:
        server.start(4)
    else:
        server.start()
    
    tornado.ioloop.IOLoop.instance().start()

