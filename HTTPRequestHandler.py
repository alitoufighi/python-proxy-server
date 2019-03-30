import logging
from HTTPResponse import *
from HTTPRequest import *
# from mail import send_mail


class HTTPRequestHandler(object):
    HTTP_SERVER_LISTENING_PORT = 80

    @staticmethod
    def run(proxy_server, sock, addr, file):
        
        request = HTTPRequest(sock, file)
        logging.basicConfig(filename= file,format='[%(asctime)s] %(message)s', level=logging.INFO)
        host = request.get_header('Host')

        if proxy_server.is_restriction_enabled() and proxy_server.is_in_disallowed_hosts(host):
            logging.info('Bad website! Sending Email to admin.')
            sock.sendall(proxy_server.bad_response('Visiting this site is forbidden!').read())
            sock.close()
            logging.info('Socket connection with peer closed.')
            # send_mail().snd_email()
            return

        if proxy_server.is_privacy_enabled():
            request.set_header('user-agent', proxy_server.privacy_user_agent)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT))
        logging.info(f'Connection established with host {host}'
                     f'on port {HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT}.')
        server_socket.send(request.read())
        logging.info('Request sent to server.')
        response = HTTPResponse(server_socket)
        logging.info('Response read from server.')
        server_socket.close()
        logging.info('Connection with server host closed.')

        if response.is_html() and proxy_server.is_http_injection_enabled():
            response = proxy_server.body_inject(response)
            logging.info('Response injected with CN-Proxy(TM) navbar.')

        proxy_server.discharge_user(addr, response.length)

        sock.sendall(response.read())
        logging.info('Response sent back to client.')
        sock.close()
