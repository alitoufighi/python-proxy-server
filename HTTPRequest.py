import socket


class BadRequest(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        print('bad http request: {0}'.format(msg))


class IncomingHTTPRequest:
    def __init__(self, sock):
        self.socket = sock
        self.fp = sock.makefile('rb', 0)

        self.method, self.route, self.version = self.read_status()
        self.headers = self.read_headers()
        self.body = self.read_body()

        self.modify_values_for_proxy()

        print('------------------BEG OF REQUEST----------------')
        print(self.method, self.route, self.version)
        print(self.headers)
        # print(self.body)
        print('------------------END OF REQUEST----------------')

    def read_status(self):
        line = self.fp.readline()
        if not line:
            raise BadRequest('not a valid line')
        method, route, version = line.split(None, 2)
        version = version.strip()
        return method, route, version

    def read_headers(self):
        headers = {}
        while True:
            line = self.fp.readline()
            # line = line.strip()
            # print('--{0}--'.format(line))
            if line == '':
                print "EMPTY LINE!!!!! EOF?"
            if not line:
                print("wth")
                break
            if self.is_last_header(line):
                # print line, len(line)
                break
            try:
                key, value = self.extract_header(line)
            except BadRequest:
                continue
            headers[key] = value
        return headers

    def extract_header(self, line):
        i = line.find(':')
        if i < 0:
            raise BadRequest("not a valid header")
        key = line[:i].lower()
        val = line[i+1:].strip()
        return key, val

    def get_header(self, key):
        try:
            return self.headers[key.lower()]
        except KeyError:
            return None

    def is_last_header(self, line):
        return True if line in ['\r\n', '\n'] else False

    def read_body(self):
        data = ''
        # according to:
        # https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_9.0.0/com.ibm.mq.ref.dev.doc/q110660_.htm
        if self.length > 0:
            try:
                # data = self.fp.read()
                data = self.socket.recv(2048)  # up to 2kB body size
            except socket.error:
                print("Raise in read_body")
                raise
        return data

    def modify_values_for_proxy(self):
        self.version = 'HTTP/1.0'

        i = self.route.find(self.headers['host']) + len(self.headers['host'])
        self.route = self.route[i:]
        if self.route == '':

            self.route = '/'

    def read(self):
        result = '{0} {1} {2}\r\n'.format(self.method, self.route, self.version)
        for key, value in self.headers.items():
            result += '{0}: {1}\r\n'.format(key, value)
        result += '\r\n{0}\r\n'.format(self.body)
        return result

    @property
    def length(self):
        return int(self.headers['content-length']) if 'content-length' in self.headers else 0

    def set_header(self, key, val):
        self.headers[key.lower()] = val.strip()
