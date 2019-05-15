import socket
import base64
import logging

MAILSERVER = ("mail.ut.ac.ir", 25)
ENDLINE = b'\r\n'
HELOCOMMAND = b'HELO CN-Proxy\r\n'
USERNAME = b"\n"
PASSWORD = b""
MAILFROM = b"MAIL FROM: <your-mail@ut.ac.ir>\r\n"
RCPTTO = b"RCPT TO: <your-mail@gmail.com>\r\n"
DATA = b"DATA\r\n"
QUIT = b"QUIT\r\n"


class SendMail:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(MAILSERVER)
        self.rcv_msg_and_log('Connected to Mail Server: ')

    def rcv_msg_and_log(self, title):
        rcv = self.socket.recv(1024)
        logging.info(f'[MAILING] {title}: {rcv.decode()}')

    def snd_helo_msg(self):
        self.socket.send(HELOCOMMAND)
        self.rcv_msg_and_log("Response to HELO")

    def auth(self):
        auth_msg = "AUTH LOGIN\r\n"
        self.socket.send(auth_msg.encode())
        self.rcv_msg_and_log("Response to AUTH LOGIN")
        self.socket.send(base64.b64encode(USERNAME))
        self.socket.send(ENDLINE)
        self.rcv_msg_and_log("Response to Username")
        self.socket.send(base64.b64encode(PASSWORD))
        self.socket.send(ENDLINE)
        self.rcv_msg_and_log("Response to Password")

    def mail_from(self):
        self.socket.send(MAILFROM)
        self.rcv_msg_and_log("Response to MAILFROM")

    def rcpt_to(self):
        self.socket.send(RCPTTO)
        self.rcv_msg_and_log("Response to RCPTTO")

    def snd_data(self, data):
        sender = f'From: support@cnproxy.com'
        receiver = f'To: <your-mail@gmail.com>'
        subject = "Subject: [CN-Proxy(TM)] Bad request form your clients!"
        self.socket.send(DATA)
        self.rcv_msg_and_log("Response to DATA command")
        data = f'{sender}\n{receiver}\n{subject}\n\n{data}\r\n.\r\n'
        self.socket.send(data.encode())
        self.rcv_msg_and_log("Response to actual data")

    def quit_msg(self):
        self.socket.send(QUIT)
        self.rcv_msg_and_log("Response to QUIT")

    def snd_email(self, data):
        self.snd_helo_msg()
        self.auth()
        self.mail_from()
        self.rcpt_to()
        self.snd_data(data)
        self.quit_msg()
        self.socket.close()
