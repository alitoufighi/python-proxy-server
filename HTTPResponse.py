import logging


class BadResponse(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        print(f'bad http response: {msg}')


class RawHTTPResponse:
    
    def __init__(self, version=None, status=None, reason=None, headers=None, body=''):
        self.version = version
        self.status = status
        self.reason = reason
        self.headers = {} if headers is None else headers
        self.body = body

    def extract_header(self, line):
        i = line.find(':')
        if i < 0:
            raise BadResponse("not a valid header")
        key = line[:i].lower()
        val = line[i+1:].strip()
        return key, val

    def get_html_encoding(self):
        content_type = self.headers['content-type'].lower().split(';')
        content_type = [s.strip() for s in content_type]
        for item in content_type:
            if 'charset' in item:
                charset = item.split('=')[1]
                return charset
        return 'utf-8'

    def _set_html_encoding(self, encoding):
        content_type = self.headers['content-type'].lower().split(';')
        content_type = [s.strip() for s in content_type]
        for index, item in enumerate(content_type):
            if 'charset' in item:
                i = item.find('=')
                content_type[index] = item.replace(item[i+1:], encoding)
                break
        self.headers['content-type'] = "; ".join(content_type)

    def is_html(self):
        return 'text/html' in self.headers['content-type'] if\
            ('content-type' in self.headers) else False

    def read(self):
        if self.is_html():
            self._set_html_encoding('utf-8')

        result = f'{self.version} {self.status} {self.reason}\r\n'
        for key, value in self.headers.items():
            result += f'{key}: {value}\r\n'
        result += f'\r\n{self.body}\r\n'
        logging.info(result)
        return result.encode(self.encoding)

    @property
    def length(self):
        return int(self.headers['content-length']) if 'content-length' in self.headers else None

    @property
    def encoding(self):
        if self.is_html():
            encoding = self.get_html_encoding()
        else:
            encoding = HTTPResponse.DEFAULT_ENCODING
        return encoding


class HTTPResponse(RawHTTPResponse):

    DEFAULT_ENCODING = "iso-8859-1"

    def __init__(self, sock):
        RawHTTPResponse.__init__(self)
        self.socket = sock
        self.fp = sock.makefile('rb', 0)

        self.version, self.status, self.reason = self._read_status()
        self.reason = self.reason.strip()
        self.headers = self._read_headers()
        self.body = self._read_body()

    def _safe_read(self, length):
        s = []
        while length > 0:
            chunk = self.fp.read(min(length, 1048576))
            if not chunk:
                break
            s.append(chunk)
            length -= len(chunk)
        return b"".join(s)

    def _read_body(self):
        if self.length is None:
            s = self.fp.read()
        else:
            s = self._safe_read(self.length)
        return s.decode(self.encoding)

    def _read_headers(self):
        headers = {}
        while True:
            line = self.fp.readline().decode(HTTPResponse.DEFAULT_ENCODING)
            if not line:
                print("bmiri-bi adab")
                break
            if self._is_last_header(line):
                break
            try:
                key, value = self.extract_header(line)
            except BadResponse:
                continue
            headers[key] = value
        return headers

    def _is_last_header(self, line):
        return True if line in ['\r\n', '\n'] else False

    def _read_status(self):
        line = self.fp.readline().decode(HTTPResponse.DEFAULT_ENCODING)
        if not line:
            raise BadResponse('not a valid line')
        try:
            version, status, reason = line.split(None, 2)
        except ValueError:
            version, status = line.split(None, 1)
            reason = ""
        try:
            status = int(status)
        except ValueError:
            raise BadResponse('not a valid status number')

        return version, status, reason
