alitou@kubuntou ~/v/s/c/mail> telnet mail.ut.ac.ir 25
Trying 80.66.177.10...
Connected to mail.ut.ac.ir.
Escape character is '^]'.
220 mail.ut.ac.ir ESMTP Postfix
HELO localhost
250 mail.ut.ac.ir
AUTH LOGIN
334 VXNlcm5hbWU6
YWxpdG91ZmlnaGkK
334 UGFzc3dvcmQ6
ODEwNkFqMjU2
235 2.7.0 Authentication successful
MAIL FROM: <alitoufighi@ut.ac.ir>
250 2.1.0 Ok
RCPT TO: <alitoumob@gmail.com>
250 2.1.5 Ok
DATA
354 End data with <CR><LF>.<CR><LF>
From: <Maede.d.z@gmail.com>
To: <alitoumob@gmail.com>
Subject: HMMMMMMMMMMMMMMMMMMM!

Is this a text? ln1
ln2

.
250 2.0.0 Ok: queued as 9396F1DA8DC
QUIT
221 2.0.0 Bye
Connection closed by foreign host.



PYTHON2.7:
In [2]: base64.b64encode("alitoufighi\n")
Out[2]: 'YWxpdG91ZmlnaGkK'

In [3]: base64.b64encode("8106Aj256")
Out[3]: 'ODEwNkFqMjU2'

