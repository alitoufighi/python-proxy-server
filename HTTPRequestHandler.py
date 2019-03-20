from HTTPResponse import *
from HTTPRequest import *
# from email import send_mail

HTTP_SERVER_LISTENING_PORT = 80

class HTTPRequestHandler(object):
    @staticmethod
    def run(proxy_server, sock, addr):
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

        if proxy_server.is_privacy_enabled():
            req.set_header('user-agent', proxy_server.privacy_user_agent)

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((host, HTTP_SERVER_LISTENING_PORT))
        new_socket.send(req.read())

        response = HTTPResponse(new_socket)
        new_socket.close()

        proxy_server.discharge_user(addr, response.length)

        sock.sendall(response.read())
        sock.close()
