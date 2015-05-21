#!/usr/bin/python
#coding=utf-8
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
#import re
import urllib
from abc import ABCMeta, abstractmethod

class DispatcherHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print 'client:', self.client_address, 'reuest path:', self.path, \
				'command:', self.command
		#query = urllib.splitquery(self.path)
		query= self.path.split('?', 1)
		action = query[0]
		params = {}
		if len(query) == 2:
			for key_value in query[1].split('&'):
				kv = key_value.split('=')
				if len(kv) == 2:
					params[kv[0]] = urllib.unquote(kv[1]).decode("utf-8", "ignore")
		buf = {"result": 1, "params": params}
		self.protocal_version = "HTTP/1.1"
		self.send_response(200)
		self.send_header("Content-type", "application/json; charset=UTF-8")
		#self.send_header("Content-type", "test/html; charset=UTF-8")
		self.send_header("Pragma", "no-cache")
		self.send_header("Cache-Control", "no-cache")
		self.end_headers()
		self.wfile.write(buf)

	def do_POST(self):
		self.send_error(404)

class Job():
	__metaclass__ = ABCMeta
	@abstractmethod
	def action(self, params):
		pass
class RunCar(Job):
	#子类必须实现父类的抽象方法，否则实例化时会报错
	def action(self, params):
		pass


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
	pass

if __name__ == "__main__":
	PORT_NUM = 8899
	serverAddress = ("", PORT_NUM)
	#server = ThreadingHttpServer(serverAddress, DispatcherHandler)
	server = HTTPServer(serverAddress, DispatcherHandler)
	print 'Started httpserver on port: ', PORT_NUM
	try:
		server.serve_forever()
	except KeyboardInterrupt, e:
		server.socket.close()
		print 'Exit...'
