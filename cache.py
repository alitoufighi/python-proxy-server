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

    def set_sockets(self, server_sock):
        self.server = server_sock

    def set_port(self, port, sock):
        self.port = port
        self.sock = sock

    def handle_modified(self, date, method, route, version, host, cache):
        logging.info("Checking for modification in cache")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, self.port))
                    
        packet = f'{method} {route} {"HTTP/1.0"}\r\n'
        packet += f'"Host": {host}\r\n'
        packet += f'"if-modified-since": {cache.modifiedsince}\r\n\r\n\r\n'

        try:
            self.server.sendall(packet.encode(HTTPRequest.DEFAULT_ENCODING))
        except OSError:
            print(self.server)
        response = HTTPResponse(self.server)
        data = response.read()
        
        if response.status == 304:
            logging.info("304 returned from server")
            cache.modifiedsince = datetime.datetime.now()
            logging.info("sending data in cache to the client")
            self.sock.sendall(cache.response)
        else:
            logging.info("not 304 returned from server")
            c = CachedObject(data, response.pragma, response.modified_since, response.expire, host, route)
            self.cachelist.remove(cache)
            self.cachelist.append(c)
            logging.info("sending updated data to the client")
            self.sock.sendall(c.response)

    def _find_cache(self, host, method, route, version):
        
        for c in self.cachelist:
            if c.host == host and c.route == route:
                logging.info("Cache Hit")
                self.cachelist.remove(c)
                self.cachelist.append(c)
                if c.expire is None:
                    logging.info("Expire header is not set.")
                    self.handle_modified(c.modifiedsince, method, route, version, host, c)
                else:
                    if datetime.datetime.strptime(c.expire, "%a, %d %b %Y %H:%M:%S GMT") >= datetime.datetime.now():
                        self.sock.sendall(c.response)
                    else:
                        self.handle_modified(c.modifiedsince, method, route, version, host, c)
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
