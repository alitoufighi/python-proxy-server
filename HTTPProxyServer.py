import struct
import sys
import socket
import json
import thread
from HTTPRequestHandler import HTTPRequestHandler

DEBUG = True

PORT = int(sys.argv[1]) if DEBUG else 8000
CONFIG_FILENAME = 'config.json'


class HTTPProxyServer:
    def __init__(self):
        self.CONFIG = self.read_config()
        self.users = self.CONFIG['accounting']['users']
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = PORT if DEBUG else self.CONFIG['port']
        # ip_addr = '127.0.0.1' if DEBUG else socket.gethostbyname(socket.gethostname())
        # TODO: gethostbyname() doesn't return 127.0.0.1 (what to do?)
        ip_addr = '127.0.0.1'
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
        #                        struct.pack('ii', 1, 0))
        self.socket.bind((ip_addr, port))
        self.socket.listen(64)

    def is_logging_enabled(self):
        return self.CONFIG['logging']['enable']

    def is_caching_enabled(self):
        return self.CONFIG['caching']['enable']

    def is_http_injection_enabled(self):
        return self.CONFIG['HTTPInjection']['enable']

    def is_privacy_enabled(self):
        return self.CONFIG['privacy']['enable']

    @property
    def log_file(self):
        return self.CONFIG['logging']['logFile']

    @property
    def cache_size(self):
        return self.CONFIG['caching']['size']

    @property
    def http_injection_body(self):
        return self.CONFIG['HTTPInjection']['post']['body']

    @property
    def privacy_user_agent(self):
        return self.CONFIG['privacy']['userAgent']

    @staticmethod
    def read_config():
        with open(CONFIG_FILENAME) as f:
            cfg = json.load(f)
        return cfg

    def is_allowed_user(self, ip_addr):
        for user in self.users:
            if ip_addr == user['IP']:
                return True
        return False

    def discharge_user(self, ip_addr, amount):
        for user in self.users:
            if user['IP'] == ip_addr:
                print("--user found! DISCHARGING {0} KILOBYTES".format(amount))
                user['volume'] = int(user['volume']) - amount
                print("--NEW HAJM: {0}".format(user['volume']))
                return
        else:
            print "NO USER FOUND?!?!"

    @property
    def config(self):
        return self.CONFIG

    def is_restriction_enabled(self):
        return self.CONFIG['restriction']['enable']

    def is_in_disallowed_hosts(self, host):
        restriction = self.CONFIG['restriction']
        # if restriction['enable'] is False:
        #     return False
        targets = restriction['targets']
        for target in targets:
            if target['notify'] is True and host in target['URL']:
                return True
        return False

    def run(self):
        while True:
            (client_socket, (address, _)) = self.socket.accept()
            if not self.is_allowed_user(address):
                print "-Refusing Connection! Disallowed User IP Address."
                client_socket.close()
                return
            print "-Connection Established."
            thread.start_new_thread(HTTPRequestHandler.run, (self, client_socket, address,))


if __name__ == '__main__':
    proxy = HTTPProxyServer()
    proxy.run()
