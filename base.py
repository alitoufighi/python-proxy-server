import socket
import time
from threading import Thread

PORT = 8000


class HTTPRequest:
    def __init__(self, data):
        data = data.decode('utf-8').split('\r\n')
        self.type = ''
        self.headers = {}
        for index, item in enumerate(data):
            if index == 0:
                self.type, self.route, self.version = item.split(' ')
            elif item != '':
                header_type, header_value = item.split(': ')
                self.headers[header_type] = header_value

        self.version = 'HTTP/1.0'
        index = self.route.find(self.headers['Host']) + len(self.headers["Host"])
        self.route = self.route[index:]
        print(self.type, self.route, self.version)
        print(self.headers)

    def get_headers(self):
        return self.headers

    def join_string(self):
        result = f'{self.type} {self.route} {self.version}\r\n'
        for key, value in self.headers.items():
            result += f'{key}: {value}\r\n'
        result += '\r\n'
        return result


class ClientThread(Thread):
    def __init__(self, s):
        Thread.__init__(self)
        self.socket = s

    def run(self):
        # try:
        data = self.socket.recv(64000000)
        req = HTTPRequest(data)
        host = req.get_headers()['Host']
        newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newsocket.connect((host, 80))
        newsocket.send(req.join_string().encode())
        print("SENT")
        retval = newsocket.recv(640000000)
        print(f'-------------{retval}------------')
        self.socket.send(retval)
        # except:
        #     pass
        self.socket.close()

        # print(data)


class HTTPProxyServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', PORT))
        self.socket.listen(5)

    def run(self):
        while True:
            (clientsocket, address) = self.socket.accept()
            print("NEW CONNECTION")
            ct = ClientThread(clientsocket)
            ct.run()
            time.sleep(1)


proxy = HTTPProxyServer()
proxy.run()
