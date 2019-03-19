
class BadRequest(Exception):
    pass


class HTTPRequest:
    def __init__(self, data):
        if data == '':
            print("WHAT IS WRONG WITH YOU?")
            raise BadRequest()
        data = data.split('\r\n')
        self.body = ''
        self.headers = {}
        body_next = False
        for index, item in enumerate(data):
            if index == 0:
                self.type, self.route, self.version = item.split(' ', 3)
            elif body_next:
                self.body = item
            elif item == '':
                body_next = True
            else:
                header_type, header_value = item.split(': ')
                self.headers[header_type] = header_value

        self.version = 'HTTP/1.0'
        index = self.route.find(self.headers['Host']) + len(self.headers['Host'])
        self.route = self.route[index:]
        if self.route == '':
            print("BAD ROUTE!")
            self.route = '/'
        print(self.type, self.route, self.version)
        print(self.headers)
        print(self.body)

    def get_headers(self):
        return self.headers

    def join_string(self):
        result = '{0} {1} {2}\r\n'.format(self.type, self.route, self.version)
        for key, value in self.headers.items():
            result += '{0}: {1}\r\n'.format(key, value)
        result += '\r\n{0}\r\n'.format(self.body)
        return result
