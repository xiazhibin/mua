import socket
from io import StringIO
import sys
from datetime import *

class WSGIServer(object):
	address_family = socket.AF_INET
	socket_type = socket.SOCK_STREAM
	request_queue_size = 1

	def __init__(self,server_address):
		self.listen_socket  = listen_socket = socket.socket(
			self.address_family,
			self.socket_type
			)

		listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		listen_socket.bind(server_address)

		listen_socket.listen(self.request_queue_size)

		host,port = self.listen_socket.getsockname()[:2]
		self.server_name = socket.getfqdn(host)
		self.server_port = port

		self.headers_set = []

	@staticmethod
	def formatTime():
		GMT_Format = "%a,%d %b %Y %H:%M:%S GMT"
		return datetime.today().strftime(GMT_Format)
		

	def set_app(self,app):
		self.application = app

	def serve_forever(self):
		listen_socket = self.listen_socket
		while True:
			self.client_connection, client_address = listen_socket.accept()
			self.handle_one_request()

	def handle_one_request(self):
		self.request_data = request_data = self.client_connection.recv(1024)
		print(''.join('< {line}\n'.format(line=line) for line in request_data.splitlines()))
		if not self.parse_request(request_data.decode('utf-8')):
			return
		env = self.get_environ()
		result = self.application(env, self.start_response)
		self.finish_response(result)

	def parse_request(self, text):
		lines = text.splitlines()
		if lines is None or len(lines) <= 0 :
			print('fuxk')
			return False
		request_line = lines[0]
		request_line = request_line.rstrip('\r\n')
		# Break down the request line into components
		(self.request_method,  # GET
		self.path,            # /hello
		self.request_version  # HTTP/1.1
		) = request_line.split()
		return True

	def get_environ(self):
		env = {}
		# The following code snippet does not follow PEP8 conventions
		# but it's formatted the way it is for demonstration purposes
		# to emphasize the required variables and their values
		#
		# Required WSGI variables
		env['wsgi.version']      = (1, 0)
		env['wsgi.url_scheme']   = 'http'
		env['wsgi.input']        = StringIO(self.request_data.decode('utf-8'))
		env['wsgi.errors']       = sys.stderr
		env['wsgi.multithread']  = False
		env['wsgi.multiprocess'] = False
		env['wsgi.run_once']     = False
		# Required CGI variables
		env['REQUEST_METHOD']    = self.request_method    # GET
		env['PATH_INFO']         = self.path              # /hello
		env['SERVER_NAME']       = self.server_name       # localhost
		env['SERVER_PORT']       = str(self.server_port)  # 8888
		return env

	def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
		server_headers = [
            ('Date', self.formatTime()),
            ('Server', 'MuaWSGIServer 0.2'),
        ]
		self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response
	
	def finish_response(self, result):
		try:
			status, response_headers = self.headers_set
			response = 'HTTP/1.1 {status}\r\n'.format(status=status)
			for header in response_headers:
				response += '{0}: {1}\r\n'.format(*header)
			response += '\r\n'
			for data in result:
				response += data.decode('utf-8')
            # Print formatted response data a la 'curl -v'
			print(''.join('> {line}\n'.format(line=line) for line in response.splitlines()))
			self.client_connection.sendall(response.encode('utf-8'))
		finally:
			self.client_connection.close()



def make_server(server_address, application):
	server = WSGIServer(server_address)
	server.set_app(application)
	return server

def run_simple(host,port,application):
	httpd = make_server((host,port), application)
	print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=port))
	httpd.serve_forever()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit('Provide a WSGI application object as module:callable')
	app_path = sys.argv[1]
	module, application = app_path.split(':')
	module = __import__(module)
	application = getattr(module, application)
	httpd = make_server(SERVER_ADDRESS, application)
	print('MuaWSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
	httpd.serve_forever()

   
