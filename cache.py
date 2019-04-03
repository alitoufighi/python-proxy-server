import logging
import socket
import datetime
from HTTPRequest import HTTPRequest
from HTTPResponse import HTTPResponse

CAPACITY = 101

class Cache:
    def __init__(self, packet, pragma, modifiedsince, expire, host):
        self.response = packet
        self.modifiedsince = modifiedsince
        self.expire = expire
        self.host = host
    
    
    
class CacheHandler:
    def __init__(self, sock, server_sock):
        self.cachelist = []    
        self.sock = sock
        self.server = server_sock
    
    def handle_modified(self, date, method, route, version, cache):
        packet = f'{method} {route} {version}\r\n'
        packet += f'{"if-modified-since"}: {date}\r\n'
        self.server.send(packet)
        response = HTTPResponse(self.server)
        data = response.read()
        if data == "304":
            cache.modifiedsince = datetime.datetime.now()
            self.sock.sendall(cache.response)
            logging.info("304 returned from server")
            logging.info("sending data in cache to the client")
        else:
            logging.info("200 returned from server")
            c = Cache()#here
            c.expire = response.expire
            c.modifiedsince = response.modified_since
            c.response = data
            c.host = cache.host
            self.cachelist.remove(cache)
            self.cachelist.append(c)
            self.sock.sendall(c.response)
            logging.info("sending updated data to the client")
        

    def _find_cache(self,host, method, route, version):
        for c in self.cachelist:
            if c.host==host:
                logging.info("Cache Hit")
                self.cachelist.insert(len(self.cachelist)-1,self.cachelist.pop(c))
                if c.expire == None:
                    self.handle_modified(method, route, version, c)#here     
                else:
                    if datetime.datetime.strptime(c.expire, "%a, %d %b %Y %H:%M:%S GMT")>=datetime.datetime.now():
                        self.sock.sendall(c.response)
                    else:
                        self.handle_modified(method, route, version, c)
                        logging.info("Expiry Expired")
                return True
        logging.info("Cache Miss")
        return False
            
                    
    def store(self, packet, pragma, modifiedsince, expire, host):
        if len(self.cachelist) > 100:
            self.cachelist.remove(0)
        if pragma == "no-cache":
            return False
        res_pkt = Cache(packet, pragma, modifiedsince, expire, host)
        self.cachelist.append(res_pkt)
        

