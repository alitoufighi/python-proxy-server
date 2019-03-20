from HTTPResponse import HTTPResponse, BadResponse
from HTTPRequest import *


class HTTPRequestHandler(object):
    @staticmethod
    def run(proxy_server, sock, addr):
        # request_data = sock.recv(2048)
        try:
            req = IncomingHTTPRequest(sock)
        except BadRequest:
            print("That was a bad request!")
            sock.close()
            return

        host = req.get_header('Host')

        if proxy_server.is_restriction_enabled() and proxy_server.is_in_disallowed_hosts(host):
            # send email to administrator
            print("SENDING EMAIL!")
            # sock.close()
            # send_mail().snd_email()
            # return

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((host, 80))
        new_socket.send(req.read())

        response = HTTPResponse(new_socket)
        new_socket.close()

        proxy_server.discharge_user(addr, response.length)

        sock.sendall(response.read())
        sock.close()
