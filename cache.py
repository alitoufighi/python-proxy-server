import logging
import socket
import datetime
from HTTPRequest import HTTPRequest
from HTTPResponse import HTTPResponse

CAPACITY = 100

class Cache:
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
        self.port= port
        self.sock = sock

    def handle_modified(self, date, method, route, version, host, cache):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, self.port))
                    
        packet = f'{method} {route} {"HTTP/1.0"}\r\n'
        packet += f'{"HOST"}: {host}\r\n'
        packet += f'{"if-modified-since"}: {cache.modifiedsince}\r\n\r\n\r\n'
        print(cache.modifiedsince)
        print("dataedateeeeeeeeeeeeee")
        print(packet)
       
        self.server.sendall(packet.encode(HTTPRequest.DEFAULT_ENCODING))
        response = HTTPResponse(self.server)
        data = response.read()
        
        if response.status == 304:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            cache.modifiedsince = datetime.datetime.now()
            self.sock.sendall(cache.response)
            logging.info("304 returned from server")
            logging.info("sending data in cache to the client")
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
            logging.info("200 returned from server")
            c = Cache(data, response.pragma, response.modified_since, response.expire, host)#here
            self.cachelist.remove(cache)
            self.cachelist.append(c)
            self.sock.sendall(c.response)
            logging.info("sending updated data to the client")
        

    def _find_cache(self,host, method, route, version):
        
        for c in self.cachelist:
            if c.host==host and c.route ==route:
                logging.info("Cache Hit")
                self.cachelist.remove(c)
                self.cachelist.append(c)
                if c.expire == None:
                    print("expire none")
                    self.handle_modified(c.modifiedsince,method, route, version, host, c)#here     
                else:
                    if datetime.datetime.strptime(c.expire, "%a, %d %b %Y %H:%M:%S GMT")>=datetime.datetime.now():
                        print("ok")
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        self.sock.sendall(c.response)
                    else:
                        self.handle_modified(c.modifiedsince,method, route, version,host, c)
                        print("Expiry Expired")
                        logging.info("Expiry Expired")
                return True
        logging.info("Cache Miss")
        return False
            
                    
    def store(self, packet, pragma, modifiedsince, expire, host, route):
        if len(self.cachelist) > CAPACITY:
            self.cachelist.remove(0)
        if pragma == "no-cache":
            return False
        res_pkt = Cache(packet, pragma, modifiedsince, expire, host, route)
        self.cachelist.append(res_pkt)
       
        

