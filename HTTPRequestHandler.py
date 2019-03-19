# import ast
import socket
import errno
# import time
import sys
# import json
# import thread
from email import send_mail
from HTTPRequest import *

# DEBUG = True

# PORT = int(sys.argv[1]) if DEBUG else 8000
# CONFIG_FILENAME = 'config.json'


# class BadRequest(Exception):
#     pass
#
#
# class HTTPRequest:
#     def __init__(self, data):
#         if data == '':
#             print("WHAT IS WRONG WITH YOU?")
#             raise BadRequest()
#         data = data.split('\r\n')
#         self.body = ''
#         self.headers = {}
#         body_next = False
#         for index, item in enumerate(data):
#             if index == 0:
#                 self.type, self.route, self.version = item.split(' ', 3)
#             elif body_next:
#                 self.body = item
#             elif item == '':
#                 body_next = True
#             else:
#                 header_type, header_value = item.split(': ')
#                 self.headers[header_type] = header_value
#
#         self.version = 'HTTP/1.0'
#         index = self.route.find(self.headers['Host']) + len(self.headers['Host'])
#         self.route = self.route[index:]
#         if self.route == '':
#             print("BAD ROUTE!")
#             self.route = '/'
#         print(self.type, self.route, self.version)
#         print(self.headers)
#         print(self.body)
#
#     def get_headers(self):
#         return self.headers
#
#     def join_string(self):
#         result = '{0} {1} {2}\r\n'.format(self.type, self.route, self.version)
#         for key, value in self.headers.items():
#             result += '{0}: {1}\r\n'.format(key, value)
#         result += '\r\n{0}\r\n'.format(self.body)
#         return result


# class SocketTools(object):
#     @staticmethod
#     def recv_all(sock):
#         rcv_data = ''
#         while True:
#             data = sock.recv(2048)
#             if not data:
#                 break
#             rcv_data += data
#         return rcv_data


class HTTPRequestHandler(object):
    @staticmethod
    def run(proxy_server, sock):
        try:
            request_data = sock.recv(2048)
            try:
                req = HTTPRequest(request_data)
            except BadRequest:
                print("That was a bad request!")
                return

            host = req.get_headers()['Host']

            if proxy_server.is_restriction_enabled() and proxy_server.is_in_disallowed_hosts(host):
                # send email to administrator
                print("SENDING EMAIL!")
                sock.close()
                # send_mail().snd_email()
                return

            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.connect((host, 80))
            new_socket.send(req.join_string().encode())

            # received_data = SocketTools.recv_all(new_socket)
            received_data = ''
            while True:
                try:
                    data = new_socket.recv(2048)
                except socket.error as e:
                    if e.errno != errno.ECONNRESET:
                        raise
                    break
                if not data:
                    break
                received_data += data

            new_socket.close()
            sock.sendall(received_data)
        except socket.timeout:
            print("---SOCKET TIMEOUT---")
        sock.close()


# class HTTPProxyServer:
#     def __init__(self):
#         self.CONFIG = self.read_config()
#         self.users = self.CONFIG['accounting']['users']
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         port = PORT if DEBUG else self.CONFIG['port']
#         # ip_addr = '127.0.0.1' if DEBUG else socket.gethostbyname(socket.gethostname())
#         # TODO: gethostbyname() doesn't return 127.0.0.1 (what to do?)
#         ip_addr = '127.0.0.1'
#         self.socket.bind((ip_addr, port))
#         self.socket.listen(64)
#
#     def is_logging_enabled(self):
#         return self.CONFIG['logging']['enable']
#
#     def is_caching_enabled(self):
#         return self.CONFIG['caching']['enable']
#
#     def is_http_injection_enabled(self):
#         return self.CONFIG['HTTPInjection']['enable']
#
#     def is_privacy_enabled(self):
#         return self.CONFIG['privacy']['enable']
#
#     @property
#     def log_file(self):
#         return self.CONFIG['logging']['logFile']
#
#     @property
#     def cache_size(self):
#         return self.CONFIG['caching']['size']
#
#     @property
#     def http_injection_body(self):
#         return self.CONFIG['HTTPInjection']['post']['body']
#
#     @property
#     def privacy_user_agent(self):
#         return self.CONFIG['privacy']['userAgent']
#
#     @staticmethod
#     def read_config():
#         with open(CONFIG_FILENAME) as f:
#             cfg = json.load(f)
#         return cfg
#
#     def is_allowed_user(self, ip_addr):
#         for user in self.users:
#             if ip_addr == user['IP']:
#                 return True
#         return False
#
#     def discharge_user(self, ip_addr, amount):
#         for user in self.users:
#             if user['IP'] == ip_addr:
#                 user['volume'] = float(user['volume']) - amount  # TODO: float or int?
#
#     @property
#     def config(self):
#         return self.CONFIG
#
#     def is_restriction_enabled(self):
#         return self.CONFIG['restriction']['enable']
#
#     def is_in_disallowed_hosts(self, host):
#         # print("-LOOKING FOR {0} IN TARGETS".format(host))
#         restriction = self.CONFIG['restriction']
#         # if restriction['enable'] is False:
#         #     return False
#         targets = restriction['targets']
#         for target in targets:
#             if target['notify'] is True and host in target['URL']:
#                 return True
#         return False
#
#     def run(self):
#         while True:
#             (client_socket, address) = self.socket.accept()
#             thread.start_new_thread(ClientThread.run, (self, client_socket,))


