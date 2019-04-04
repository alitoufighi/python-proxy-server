import logging
from HTTPResponse import *
from HTTPRequest import *
from mail import SendMail


class HTTPRequestHandler(object):
    HTTP_SERVER_LISTENING_PORT = 80

    @staticmethod
    def run(proxy_server, sock, addr):
        
        request = HTTPRequest(sock)
        host = request.get_header('Host')

        if proxy_server.is_restriction_enabled() and proxy_server.is_in_disallowed_hosts(host):
            logging.info('Bad website! Sending Email to admin.')
            sock.sendall(proxy_server.bad_response('Visiting this site is forbidden!').read())
            sock.close()
            logging.info('Socket connection with peer closed.')
            SendMail().snd_email(request.read().decode(request.DEFAULT_ENCODING))
            return

        if proxy_server.is_privacy_enabled():
            request.set_header('user-agent', proxy_server.privacy_user_agent)
        proxy_server.cache_handler.set_port(HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT, sock)
        if not proxy_server.cache_handler._find_cache(host, request.method, request.route, request.version):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT))
            logging.info(f'Connection established with host {host}'
                         f'on port {HTTPRequestHandler.HTTP_SERVER_LISTENING_PORT}.')
            server_socket.send(request.read())
            logging.info('Request sent to server.')
            response = HTTPResponse(server_socket)
            logging.info('Response read from server.')
            logging.info('Connection with server host closed.')
            if response.is_html() and proxy_server.is_http_injection_enabled():
                response = proxy_server.body_inject(response)
                logging.info('Response injected with CN-Proxy(TM) navbar.')
            proxy_server.discharge_user(addr, response.length)
            res = response.read()
            sock.sendall(res)
            if proxy_server.is_caching_enabled():
                proxy_server.cache_handler.set_sockets(server_socket)
                proxy_server.cache_handler.store(res, response.pragma, response.modified_since, response.expire, host, request.route)
            logging.info('Response sent back to client.')
            server_socket.close()
        sock.close()
