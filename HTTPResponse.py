
class BadResponse(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        print('bad http response: {0}'.format(msg))


class HTTPResponse:

    DEFAULT_ENCODING = "iso-8859-1"

    def __init__(self, sock):
        self.socket = sock
        self.fp = sock.makefile('rb', 0)

        self.version, self.status, self.reason = self.read_status()
        self.reason = self.reason.strip()
        self.headers = self.read_headers()
        self.body = self.read_body()

        # print('------------------BEG OF RESPONSE----------------')
        # print(self.version, self.status, self.reason)
        # print(self.headers)
        # print(self.body)
        # print('------------------END OF RESPONSE----------------')

    def safe_read(self, length):
        s = []
        while length > 0:
            chunk = self.fp.read(min(length, 1048576))
            if not chunk:
                break
            s.append(chunk)
            length -= len(chunk)
        return b"".join(s)

    def read_body(self):
        if self.length is None:
            s = self.fp.read()
        else:
            s = self.safe_read(self.length)
        return s.decode(self.encoding)

    def read_headers(self):
        headers = {}
        while True:
            line = self.fp.readline().decode(HTTPResponse.DEFAULT_ENCODING)
            if not line:
                print("wth")
                break
            if self.is_last_header(line):
                break
            try:
                key, value = self.get_header(line)
            except BadResponse:
                continue
            headers[key] = value
        return headers

    def get_header(self, line):
        i = line.find(':')
        if i < 0:
            raise BadResponse("not a valid header")
        key = line[:i].lower()
        val = line[i+1:].strip()
        return key, val

    def is_last_header(self, line):
        return True if line in ['\r\n', '\n'] else False

    def read_status(self):
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

    def get_html_encoding(self):
        content_type = self.headers['content-type'].lower().split(';')
        content_type = [s.strip() for s in content_type]
        for item in content_type:
            if 'charset' in item:
                charset = item.split('=')[1]
                return charset

    def is_html(self):
        return 'text/html' in self.headers['content-type'] if\
            ('content-type' in self.headers and 200 <= self.status < 300) else False

    def read(self):
        result = '{0} {1} {2}\r\n'.format(self.version, self.status, self.reason)
        for key, value in self.headers.items():
            result += '{0}: {1}\r\n'.format(key, value)
        result += '\r\n{0}\r\n'.format(self.body)
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
