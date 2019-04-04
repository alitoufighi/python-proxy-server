import logging
import socket
import datetime
from HTTPRequest import HTTPRequest
from HTTPResponse import HTTPResponse

CAPACITY = 100


class CachedObject:
    def __init__(self, packet, pragma, modifiedsince, expire, host, route):
        self.response = packet
        self.modifiedsince = modifiedsince
        self.expire = expire
        self.host = host
        self.route = route
    

class CacheHandler:
    def __init__(self):
        self.cachelist = []

    def handle_modified(self, date, method, route, version, host, cache, sock):
        logging.info("Checking for modification in cache")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, 80))
                    
        packet = f'{method} {route} HTTP/1.0\r\n'
        packet += f'Host: {host}\r\n'
        packet += f'if-modified-since: {cache.modifiedsince}\r\n\r\n\r\n'

        server_socket.sendall(packet.encode(HTTPRequest.DEFAULT_ENCODING))
        response = HTTPResponse(server_socket)
        server_socket.close()
        data = response.read()
        if response.status == 304:
            logging.info("304 returned from server")
            cache.modifiedsince = datetime.datetime.now()
            logging.info("sending data in cache to the client")
            sock.sendall(cache.response)
        else:
            logging.info("not 304 returned from server")
            c = CachedObject(data, response.pragma, response.modified_since, response.expire, host, route)
            self.cachelist.remove(cache)
            self.cachelist.append(c)
            logging.info("sending updated data to the client")
            sock.sendall(c.response)

    def is_cached(self, host, method, route, version, sock):
        for c in self.cachelist:
            if c.host == host and c.route == route:
                logging.info("Cache Hit")
                self.cachelist.remove(c)
                self.cachelist.append(c)
                if c.expire is None:
                    logging.info("Expire header is not set.")
                    self.handle_modified(c.modifiedsince, method, route, version, host, c, sock)
                else:
                    if datetime.datetime.strptime(c.expire, "%a, %d %b %Y %H:%M:%S GMT") >= datetime.datetime.now():
                        sock.sendall(c.response)
                    else:
                        self.handle_modified(c.modifiedsince, method, route, version, host, c, sock)
                        logging.info("Expiry Expired")
                return True
        logging.info("Cache Miss")
        return False
                    
    def store(self, packet, pragma, modifiedsince, expire, host, route):
        if pragma == "no-cache":
            return
        if len(self.cachelist) > CAPACITY:
            del self.cachelist[0]
        res_pkt = CachedObject(packet, pragma, modifiedsince, expire, host, route)
        self.cachelist.append(res_pkt)
