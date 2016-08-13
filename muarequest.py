import argparse
import errno
import os
import socket


SERVER_ADDRESS = 'localhost', 8888
REQUEST = b"""\
GET / HTTP/1.1
Host: localhost:8888
Cookie: id=bin; uuid=123456

haha
"""

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(SERVER_ADDRESS)
	sock.sendall(REQUEST)         

if __name__ == '__main__':
	main()
