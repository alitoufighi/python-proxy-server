import sys
import socket
import json
import _thread
from HTTPRequestHandler import HTTPRequestHandler

DEBUG = True

PORT = int(sys.argv[1]) if DEBUG else 8000
CONFIG_FILENAME = 'config.json'


class HTTPProxyServer:

    class HTMLTools:
        """
            a tiny tool to insert a little navbar to html pages received by this proxy server
        """
        def __init__(self, text):
            self.html = """\n
                <ul class="cn-proxy">
                    <li class="cn-proxy">
                        <p class="cn-proxy">{0}</p>
                    </li>
                </ul>""".format(text)
            self.css = open('navbar.css', 'r').read()

        def add_navbar(self, html):
            css_added = self.add_navbar_css(html)
            html_added = self.add_navbar_html(css_added)
            return html_added

        def add_navbar_css(self, html):
            insertion_index = html.find('</style>')
            if insertion_index < 0:
                insertion_index = html.find('</head>')
                insertion_text = """\n
                    <style>
                        {0}
                    </style>
                """.format(self.css)
            else:
                insertion_text = self.css
            return self.insert_str(html, insertion_text, insertion_index)

        def add_navbar_html(self, html):
            i = html.find('<body')
            insertion_index = i + html[i:].find('>') + 1
            # regexp to find enclosing of tags
            return self.insert_str(html, self.html, insertion_index)

        @staticmethod
        def insert_str(source_str, insert_str, pos):
            return source_str[:pos] + insert_str + source_str[pos:]

    def __init__(self):
        self.CONFIG = self.read_config()
        self.users = self.CONFIG['accounting']['users']
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = PORT if DEBUG else self.CONFIG['port']
        ip_addr = '127.0.0.1'
        self.socket.bind((ip_addr, port))
        print("-Starting proxy server on {0}:{1}".format(ip_addr, port))
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
        if amount is None:
            return
        for user in self.users:
            if user['IP'] == ip_addr:
                user['volume'] = int(user['volume']) - amount
                return

    def has_charge(self, ip_addr):
        for user in self.users:
            if user['IP'] == ip_addr:
                return int(user['volume']) > 0
        return False

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

    def body_inject(self, html):
        return HTTPProxyServer.HTMLTools(self.http_injection_body).add_navbar(html)

    def run(self):
        while True:
            (client_socket, (address, _)) = self.socket.accept()
            if not self.is_allowed_user(address):
                print("-Refusing Connection! Disallowed User IP Address.")
                client_socket.close()
                return
            if not self.has_charge(address):
                print("-Refusing Connection! User Has No Charge.")
                return
            print("-Connection Established.")
            _thread.start_new_thread(HTTPRequestHandler.run, (self, client_socket, address,))


if __name__ == '__main__':
    proxy = HTTPProxyServer()
    proxy.run()
