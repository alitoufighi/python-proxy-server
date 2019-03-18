# import ast
import socket
import errno
# import time
import sys
import json
import thread
from email import send_mail

PORT = int(sys.argv[1])
CONFIG_FILENAME = 'config.json'
CONFIG = {}


class BadRequest(Exception):
    pass


class HTTPRequest:
    def __init__(self, data):
        if data == '':
            print("WHAT IS WRONG WITH YOU?")
            raise BadRequest()
        data = data.split('\r\n')
        print(data)
        self.body = ''
        self.headers = {}
        body_next = False
        for index, item in enumerate(data):
            if index == 0:
                self.type, self.route, self.version = item.split(' ', 3)
            elif body_next:
                self.body = item
            elif item == '':
                body_next = True
            else:
                header_type, header_value = item.split(': ')
                self.headers[header_type] = header_value

        self.version = 'HTTP/1.0'
        index = self.route.find(self.headers['Host']) + len(self.headers['Host'])
        self.route = self.route[index:]
        if self.route == '':
            self.route = '/'
        print(self.type, self.route, self.version)
        print(self.headers)
        print(self.body)

    def get_headers(self):
        return self.headers

    def join_string(self):
        result = '{0} {1} {2}\r\n'.format(self.type, self.route, self.version)
        for key, value in self.headers.items():
            result += '{0}: {1}\r\n'.format(key, value)
        result += '\r\n{0}\r\n'.format(self.body)
        return result


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


class ClientThread(object):
    @staticmethod
    def run(sock):
        try:
            request_data = sock.recv(2048)
            try:
                req = HTTPRequest(request_data)
            except BadRequest:
                print("That was a bad request!")
                return

            host = req.get_headers()['Host']

            if HTTPProxyServer.is_in_disallowed_hosts(host):  # send email to administrator
                print("SENDING EMAIL!")
                send_mail().snd_email()
                sock.close()
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


class HTTPProxyServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', PORT))
        self.socket.listen(64)

    @staticmethod
    def read_config():
        global CONFIG
        with open(CONFIG_FILENAME) as f:
            CONFIG = json.load(f)
        print(CONFIG)

    @staticmethod
    def is_in_disallowed_hosts(host):
        print("-LOOKING FOR {0} IN TARGETS".format(host))
        restriction = CONFIG['restriction']
        if restriction['enable'] is not True:
            return False
        targets = restriction['targets']
        for target in targets:
            print(target)
            if host in target['URL'] and target['notify'] == 'true':
                return True
        return False

    def run(self):
        while True:
            (client_socket, address) = self.socket.accept()
            thread.start_new_thread(ClientThread.run, (client_socket,))


HTTPProxyServer.read_config()
proxy = HTTPProxyServer()
proxy.run()
