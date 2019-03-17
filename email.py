import socket
import base64
import time


MAILSERVER = ("alt4.gmail-smtp-in.l.google.com", 25)
HELOCOMMAND = 'HELO Maede\r\n'
USERNAME = "maede.d.z@gmail.com\n"
PASSWORD = "13770822md"
MAILFROM = "MAIL FROM:<maede.d.z@gmail.com>\r\n"
RCPTTO = "RCPT TO:<maede.77.dz@gmail.com>"
DATA = "DATA\r\n"
QUIT = "QUIT\r\n"

class send_mail:
    def __init__(self ):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(MAILSERVER)
    
    def rcv_msg_print(self, title):
        rcv = self.socket.recv(1024)
        print(title +  rcv.decode())

    def snd_helo_msg(self):
        self.socket.send(HELOCOMMAND.encode())
        self.rcv_msg_print("helo: ")

    def auth(self):
        auth_msg = "AUTHO LOGIN ".encode() + base64.b64encode(("\x00"+USERNAME+"\x00"+PASSWORD).encode()) + "\r\n".encode()
        self.socket.send(auth_msg)
        self.rcv_msg_print("auth: ")
        
    def mail_from(self):
        self.socket.send(MAILFROM.encode())
        self.rcv_msg_print("mail from: ")

    def rcpt_to(self):
        self.socket.send(RCPTTO.encode())
        self.rcv_msg_print("RCPT TO: ")

    def snd_data(self):
        self.socket.send(DATA.encode())
        self.rcv_msg_print("DATA command: ")
        msg = "Hello World!"
        self.socket.send(msg)
        self.rcv_msg_print("DATA: ")

    def quit_msg(self):
        self.socket.send(QUIT.encode())
        self.rcv_msg_print("QUIT: ")
        self.socket.close()

    def snd_email(self):
        rcv = self.socket.recv(1024)
        print("connection: " + rcv.decode())
        self.snd_helo_msg()    
        self.mail_from()
        self.auth()
        self.rcpt_to()
        self.snd_data()
        self.quit_msg()
        




email = send_mail()
email.snd_email()
