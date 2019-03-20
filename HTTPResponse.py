import socket


class BadResponse(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        print('bad http response: {0}'.format(msg))


class HTTPResponse:
    def __init__(self, sock):
        self.socket = sock
        self.fp = sock.makefile('rb', 0)

        self.version, self.status, self.reason = self.read_status()
        self.reason = self.reason.strip()
        self.headers = self.read_headers()
        self.body = self.read_body()

        print('------------------BEG OF RESPONSE----------------')
        print(self.version, self.status, self.reason)
        print(self.headers)
        # print(self.body)
        print('------------------END OF RESPONSE----------------')

    def read_body(self):
        # if self.length <= 0:
        #     return ''
        buf = []
        while True:
            try:
                data = self.socket.recv(2048)
            except socket.error as e:
                if e.args[0] == socket.EINTR:
                    continue
                print("Raise in read_body")
                raise
            if not data:
                break
            buf.append(data)
        return "".join(buf)

    def read_headers(self):
        headers = {}
        while True:
            line = self.fp.readline()
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
        line = self.fp.readline()

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

    def read(self):
        result = '{0} {1} {2}\r\n'.format(self.version, self.status, self.reason)
        for key, value in self.headers.items():
            result += '{0}: {1}\r\n'.format(key, value)
        result += '\r\n{0}\r\n'.format(self.body)
        return result

    @property
    def length(self):
        return int(self.headers['content-length']) if 'content-length' in self.headers else len(self.body)
