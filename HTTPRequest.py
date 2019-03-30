import socket
import logging

class BadRequest(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        print(f'bad http request: {msg}')


class HTTPRequest:

    DEFAULT_ENCODING = "iso-8859-1"

    def __init__(self, sock, file):
        self.socket = sock
        self.file=file
        self.fp = sock.makefile('rb', 0)
        self.method, self.route, self.version = self._read_status()
        self.headers = self._read_headers()
        self.body = self._read_body()

        self.modify_values_for_proxy()

    def _read_status(self):
        line = self.fp.readline().decode(HTTPRequest.DEFAULT_ENCODING)
        if not line:
            raise BadRequest('not a valid line')
        method, route, version = line.split(None, 2)
        version = version.strip()
        return method, route, version

    def _read_headers(self):
        headers = {}
        while True:
            line = self.fp.readline().decode(HTTPRequest.DEFAULT_ENCODING)
            if self._is_last_header(line):
                break
            try:
                key, value = self.extract_header(line)
            except BadRequest:
                continue
            headers[key] = value
        return headers

    def _is_last_header(self, line):
        return True if line in ['\r\n', '\n'] else False

    def _read_body(self):
        data = ''
        if self.length > 0:
            try:
                data = self.fp.read().decode(HTTPRequest.DEFAULT_ENCODING)
            except socket.error:
                raise BadRequest('socket error in read_body')
        return data

    def remove_accept_gzip_encoding(self):
        if not ('accept-encoding' in self.headers):
            return
        accept_encodings = self.headers['accept-encoding']
        accept_encodings = [item.strip() for item in accept_encodings.split(',')]
        try:
            accept_encodings.remove('gzip')
        except ValueError:
            pass
        self.headers['accept-encoding'] = accept_encodings

    def set_header(self, key, val):
        self.headers[key.lower()] = val.strip()

    def get_header(self, key):
        try:
            return self.headers[key.lower()]
        except KeyError:
            return None

    def extract_header(self, line):
        i = line.find(':')
        if i < 0:
            raise BadRequest("not a valid header")
        key = line[:i].lower()
        val = line[i+1:].strip()
        return key, val

    def modify_values_for_proxy(self):
        self.version = 'HTTP/1.0'

        i = self.route.find(self.headers['host']) + len(self.headers['host'])
        self.route = self.route[i:]
        if self.route == '':
            self.route = '/'
        self.remove_accept_gzip_encoding()

    def read(self):
        result = f'{self.method} {self.route} {self.version}\r\n'
        for key, value in self.headers.items():
            result += f'{key}: {value}\r\n'
        result += f'\r\n{self.body}\r\n'
        logging.basicConfig(filename=self.file,format='[%(asctime)s] %(message)s', level=logging.INFO)
        logging.info(result)
        return result.encode(HTTPRequest.DEFAULT_ENCODING)

    @property
    def length(self):
        return int(self.headers['content-length']) if 'content-length' in self.headers else 0
