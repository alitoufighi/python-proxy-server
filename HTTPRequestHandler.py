from HTTPResponse import *
from HTTPRequest import *
# from email import send_mail


class HTTPRequestHandler(object):
    HTTP_SERVER_LISTENING_PORT = 80

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
            # Send Email to Administrator
            print("-Sending Email to Admin!")

            # Uncomment lines below to make it functional
            # sock.close()
            # send_mail().snd_email()
            # return

        if proxy_server.is_privacy_enabled():
            # Privacy Mechanism
            req.set_header('user-agent', proxy_server.privacy_user_agent)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT))
        server_socket.send(req.read())

        response = HTTPResponse(server_socket)
        server_socket.close()

        if response.is_html() and proxy_server.is_http_injection_enabled():
            # HTTP-Injection
            response.body = proxy_server.body_inject(response.body)

        proxy_server.discharge_user(addr, response.length)

        sock.sendall(response.read())
        sock.close()
