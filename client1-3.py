import socket
import sys
import os

UNEXPECTED_RESPONSE = '100'
MISSING_PAGE        = '200'

class Cliente_FTP:
    def __init__(self):
        self.handle = handler()
        self.buffer_size = 1024
        self.sock_pasv = False

    def connect(self, host):
        self.sock_main = constructor(1, host)
        self.sock_main.recv()
                                 
    def think(self, thought):
        print("!!!", str(thought), '\n')

    def do_nothing(self):
        self.sock_main.relay('NOOP')

    def error(self, err, msg):
        raise err

    def LOGIN(self, usern, passw):
        self.sock_main.relay('USER '+usern)
        res = self.sock_main.relay('PASS '+passw, filt=passw)

        if self.handle.obtenerID(res) != 230:
            self.error(UNEXPECTED_RESPONSE, 'incorrect username or password')
            
    def DIR(self):
        self.PASV()
        msg = self.sock_main.relay('NLST')
        
        if self.handle.validacion(msg):

            msg = ''
            add = True
            while add != '':
                add = self.sock_pasv.recv()
                msg += add
            self.think('Empty message sent. File list is done.')

            self.sock_pasv.cls()
        
            flist = self.handle.parseNLST(msg)
            self.think(flist)
        
            self.sock_main.recv(226)

        else:
            self.sock_pasv.cls()
            flist = []
        
        return flist
        
    def SIZE(self, f):
        msg = self.sock_main.relay('SIZE '+f)
        if self.handle.validacion(msg):
            fsize = self.handle.parseTamanho(msg)
        else:
            fsize = False
        return fsize

    def CDUP(self):
        self.sock_main.relay('CDUP')

    def MODE(self, m='S'):
        self.sock_main.relay('MODE '+m)

    def TYPE(self, t='A'):        
        self.sock_main.relay('TYPE '+t)

    def STRU(self, s='F'):
        self.sock_main.relay('STRU '+s)
        
    def CWD(self, dname):
        self.sock_main.relay('CWD '+dname, 250)

    def MKD(self, dname):
        self.sock_main.relay('MKD '+dname, 257)

    def PASV(self):        

        if self.sock_pasv:
            self.think('Checking for open socket')
            assert not self.sock_pasv.open
			
        msg = self.sock_main.relay('PASV')
        newip, newport = self.handle.parsePASV(msg)


        self.sock_pasv = constructor(2, newip, newport)

        return newip, newport

    def QUIT(self):
	
        if self.sock_pasv:
            if self.sock_pasv.open:
                self.think('Passive port open... closing')
                self.sock_pasv.cls()
            else:
                self.think('Passive port already closed')
        self.sock_main.relay('QUIT')
        self.sock_main.cls()
        
    def upload(self, fname, fsource):        
        self.PASV()
        self.sock_main.relay('STOR '+fname)

        my_file = ops(fsource)
        while my_file.opened:
            self.sock_pasv.envio(my_file.next(self.buffer_size),
                                False)
								
        self.sock_pasv.cls()

        self.sock_main.recv(226)

    def upload_init(self, fname, fsource):
        self.PASV()
        self.sock_main.relay('STOR '+fname)
        my_file = ops(fsource)
        return my_file
    
    def upload_envio(self, my_file, buff):
        self.sock_pasv.envio(my_file.next(buff), False)
        return my_file.opened

    def upload_abort(self):
        self.sock_main.envio('ABOR')
        self.sock_pasv.cls()
        self.sock_main.recv(226)

    def upload_close(self):
        self.sock_pasv.cls()
        self.sock_main.recv(226)

		
class constructor:
    def __init__(self, sid, host, port=21):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.sid = str(sid)
        self.open = True
        self.handle = handler()

    def hold(self, error):
        pass

    def cls(self):
	
        if self.open:
            self.s.close()
            self.open = False

    def relay(self, mes='', expect=False, filt=''):
        self.envio(mes, True, filt)
        return self.recv(expect)

    def recv(self, expect=False):
        print(self.sid, '<<<',)
        
        try:
            rec = self.s.recv(1024)
        except socket.error:
            self.hold('Software caused connection abort')
            
        print(rec)


        if len(rec) > 3:

            if rec[3] == '-':
                return rec+self.recv()
        return rec        

    def envio(self, mes='', CRLF=True, filt=''):
        print(self.sid, '>>>',)

        try:
            self.s.envio(mes + ('', '\r\n')[CRLF==True])
           
        except socket.error:
            self.hold('Connection reset')

        if CRLF:
            if filt:
                print(mes.replace(filt, '*'*len(filt)))
            else:
                print(mes)


class handler:
    def partir(self, t, s, e):
        return t.split(s)[-1].split(e)[0]

    def obtenerID(self, msg):
        lines = msg.split('\r\n')
        return int(lines[-2].split(' ')[0])

    def parsePASV(self, msg):
        nmsg = self.partir(msg, '(', ')')
        p = nmsg.split(',')
        return '.'.join(p[:4]), int(p[4])*256 + int(p[5])

    def parseNLST(self, msg):
        if msg:
            return msg.split('\r\n')[:-1]
        else:
            return []

    def parseGeneral(self, msg):
        return self.partir(msg, ' ', '\r\n')


    def parseTamanho(self, msg):
        return self.parseGeneral(msg)

    def validacion(self, msg):
       
        if self.obtenerID(msg) in (450, 550):
            return False
        return True


class ops:
    def __init__(self, name):
        self.f = open(name, 'rb')
        self.size = os.stat(name)[6]
        self.pos = 0
        self.opened = True

    def next(self, buff=1024):
        self.f.seek(self.pos)
        self.pos += buff

        if self.pos >= self.size:
            piece = self.f.read(-1)
            self.f.close()
            self.opened = False
        else:
            piece = self.f.read(buff)
            
        return piece


if __name__ == '__main__':
    C = Cliente_FTP()
    
    try:
        C.connect(input("FTP Address: "))
        
    except socket.error:
        print("Could not connect")
        sys.exit(1)
        
    try:
        C.LOGIN(input("Username: "),
                       input("Password: "))
        
    except UNEXPECTED_RESPONSE:
        print("Incorrect login")
        sys.exit(1)
    
    C.MODE()
    C.TYPE('I')
    C.STRU()

    C.CWD('/')
    C.MKD('test')
    C.CWD('test')

    dest = 'tested.py'
    C.upload(dest, sys.argv[0])
    
    folder = C.DIR()
    fsize = C.SIZE(dest)

    C.QUIT()

    if dest in folder:
        print("'%s' uploaded to the folder.\n\n Size: %s BYTES\n"%(dest, fsize))
    else:
        print("File not upload.")
