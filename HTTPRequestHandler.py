from HTTPResponse import *
from HTTPRequest import *
# from mail import send_mail


class HTTPRequestHandler(object):
    HTTP_SERVER_LISTENING_PORT = 80

    @staticmethod
    def run(proxy_server, sock, addr):
        request = HTTPRequest(sock)

        host = request.get_header('Host')

        if proxy_server.is_restriction_enabled() and proxy_server.is_in_disallowed_hosts(host):
            print("-Sending Email to Admin!")
            sock.sendall(proxy_server.bad_response('Visiting this site is forbidden!').read())
            sock.close()
            # send_mail().snd_email()
            return

        if proxy_server.is_privacy_enabled():
            request.set_header('user-agent', proxy_server.privacy_user_agent)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT))
        server_socket.send(request.read())

        response = HTTPResponse(server_socket)
        server_socket.close()

        if response.is_html() and proxy_server.is_http_injection_enabled():
            response.body = proxy_server.body_inject(response.body)

        proxy_server.discharge_user(addr, response.length)

        sock.sendall(response.read())
        sock.close()
