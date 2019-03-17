import socket
import errno
import time
import sys
import thread
# from threading import Thread
PORT = int(sys.argv[1])


class BadRequest(Exception):
    pass


class HTTPRequest:
    def __init__(self, data):
        if data == '':
            print("WHAT THE FUCK IS WRONG WITH YOU?")
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
        index = self.route.find(self.headers['Host']) + len(self.headers["Host"])
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


# class TCPSocket:
#     def __init__(self, port=None):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         if port is not None:
#             self.socket.bind(port)
#
#     def recv_all(self):
#         rcv_data = ''
#         while True:
#             data = self.socket.recv(2048)
#             if not data:
#                 break
#             rcv_data += data
#         return rcv_data


class SocketTools:

    @staticmethod
    def recv_all(sock):
        rcv_data = ''
        while True:
            data = sock.recv(2048)
            if not data:
                break
            rcv_data += data
        return rcv_data


class ClientThread(object):
    # def __init__(self):
    #     pass
        # self.socket = s

    @staticmethod
    def run(sock):
        try:
            # print("HERE1")
            request_data = sock.recv(2048)
            # request_data = ''
            # while True:
            #     data = self.socket.recv(2048)
            #     if not data:
            #         break
            #     request_data += data
            # request_data = SocketTools.recv_all(self.socket)
            # print("_______________{0}_______________".format(request_data))
            # print()
            # print("______________________________")
            try:
                req = HTTPRequest(request_data)
            except BadRequest:
                print("That was a bad request!")
                return

            host = req.get_headers()['Host']
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.connect((host, 80))
            # print("HERE2")
            new_socket.send(req.join_string().encode())
            # print("HERE3")

            # received_data = SocketTools.recv_all(new_socket)
            received_data = ''
            while True:
                try:
                    data = new_socket.recv(2048)
                except socket.error as e:
                    if e.errno != errno.ECONNRESET:
                        raise  # Not error we are looking for
                    break  # Handle error here.
                if not data:
                    break
                received_data += data

            new_socket.close()
            # print("HERE4")
            sock.sendall(received_data)
            # print("HERE5")
        except socket.timeout:
            print("---SOCKET TIMEOUT---")
        sock.close()


class HTTPProxyServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', PORT))
        self.socket.listen(64)

    def run(self):
        while True:
            (client_socket, address) = self.socket.accept()
            # print("NEW CONNECTION")
            thread.start_new_thread(ClientThread.run, (client_socket,))
            # ct = ClientThread(client_socket)
            # ct.run()
            # time.sleep(0.1)


proxy = HTTPProxyServer()
proxy.run()
