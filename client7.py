import socket
import sys
import os
import time
import urllib2

UNEXPECTED_RESPONSE = '100'
MISSING_PAGE        = '200'

class handler: 
    def get_between(self, t, s, e):
        return t.split(s)[-1].split(e)[0]

    def get_id(self, msg):
        lines = msg.split('\r\n')
        return int(lines[-2].split(' ')[0])

    def parse_pasv(self, msg):
        nmsg = self.get_between(msg, '(', ')')
        p = nmsg.split(',')
        return '.'.join(p[:4]), int(p[4])*256 + int(p[5])

    def parse_nlst(self, msg):
        if msg:
            return msg.split('\r\n')[:-1]
        else:
            return []

    def global_parse(self, msg):
        return self.get_between(msg, ' ', '\r\n')

    def string_to_epoch(self, t, timezone):
        localtime = (int(t[:4]),
                     int(t[4:6]),
                     int(t[6:8]),int(t[8:10]),int(t[10:12]),int(t[12:14]),
                     0,0,0)
        return time.mktime(localtime)+timezone

    def parse_time(self, msg, timezone):
        string = self.global_parse(msg)
        return self.string_to_epoch(string, timezone)

    def parse_size(self, msg):
        return self.global_parse(msg)

    def validify_case(self, msg):
       
        if self.get_id(msg) in (450, 550):
            return False
        return True


class mk_socket: 
    def __init__(self, sid, host, port=21):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.sid = str(sid)
        self.open = True
        self.handle = handler()

    def hold_state(self, error):
        pass

    def cls(self):
	
        if self.open:
            self.s.close()
            self.open = False

    def relay(self, mes='', expect=False, filt=''):
        self.send(mes, True, filt)
        return self.recv(expect)

    def recv(self, expect=False):
        print self.sid, '<<<',
        
        try:
            rec = self.s.recv(1024)
        except socket.error:
            self.hold_state('Software caused connection abort')
            
        print rec


        if len(rec) > 3:

            if rec[3] == '-':
                return rec+self.recv()
        return rec        

    def send(self, mes='', CRLF=True, filt=''):
        print self.sid, '>>>',

        try:
            self.s.send(mes + ('', '\r\n')[CRLF==True])
           
        except socket.error:
            self.hold_state('Connection reset')

        if CRLF:
            if filt:
                print mes.replace(filt, '*'*len(filt))
            else:
                print mes


class open_slow:
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

		
class ftp_client:
    def __init__(self):
        self.handle = handler()

        self.timezone = 0

        self.buffer_size = 1024

        self.sock_pasv = False

    def connect(self, host):
        self.sock_main = mk_socket(1, host)
        self.sock_main.recv()

    def set_time(self, page):
        ip, port = self.PASV()
        try:
            self.think('Synchronizing time...')
            opener = urllib2.build_opener()
            t1 = int(opener.open('http://'+ip+'/'+page).read())
            t2 = time.time()
            self.timezone = t2 - (t1 + 3600*5)
            self.think('Time zone set to %s seconds'%self.timezone)
            time.sleep(0.5)
            
        except Exception, msg:
            self.error(MISSING_PAGE, 'was unable to synchronize time')

        self.sock_pasv.cls()

    def set_timezone(self, h):
        self.timezone = h*3600
                                 
    def think(self, thought):
        print "!!!", str(thought), '\n'

    def do_nothing(self):
        self.sock_main.relay('NOOP')

    def error(self, err, msg):
        raise err

    def LOGIN(self, usern, passw):
        self.sock_main.relay('USER '+usern)
        res = self.sock_main.relay('PASS '+passw, filt=passw)

        if self.handle.get_id(res) != 230:
            self.error(UNEXPECTED_RESPONSE, 'incorrect username or password')
            
    def DIR(self):
        self.PASV()
        msg = self.sock_main.relay('NLST')
        
        if self.handle.validify_case(msg):

            msg = ''
            add = True
            while add != '':
                add = self.sock_pasv.recv()
                msg += add
            self.think('Empty message sent. File list is done.')

            self.sock_pasv.cls()
        
            flist = self.handle.parse_nlst(msg)
            self.think(flist)
        
            self.sock_main.recv(226)

        else:
            self.sock_pasv.cls()
            flist = []
        
        return flist
        
    def SIZE(self, f):
        msg = self.sock_main.relay('SIZE '+f)
        if self.handle.validify_case(msg):
            fsize = self.handle.parse_size(msg)
        else:
            fsize = False
        return fsize

    def TIME(self, f):
        msg = self.sock_main.relay('MDTM '+f)
        if self.handle.validify_case(msg):
            ftime = self.handle.parse_time(msg, self.timezone)
        else:
            ftime = False
        return ftime

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
        newip, newport = self.handle.parse_pasv(msg)


        self.sock_pasv = mk_socket(2, newip, newport)

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

        my_file = open_slow(fsource)
        while my_file.opened:
            self.sock_pasv.send(my_file.next(self.buffer_size),
                                False)
								
        self.sock_pasv.cls()

        self.sock_main.recv(226)

    def upload_init(self, fname, fsource):
        self.PASV()
        self.sock_main.relay('STOR '+fname)
        my_file = open_slow(fsource)
        return my_file
    
    def upload_send(self, my_file, buff):
        self.sock_pasv.send(my_file.next(buff), False)
        return my_file.opened

    def upload_abort(self):
        self.sock_main.send('ABOR')
        self.sock_pasv.cls()
        self.sock_main.recv(226)

    def upload_close(self):
        self.sock_pasv.cls()
        self.sock_main.recv(226)


if __name__ == '__main__':

    MYclient = ftp_client()
    
    try:
        MYclient.connect(raw_input("FTP Address: "))
        
    except socket.error:
        print "Could not connect"
        sys.exit(1)
        
    try:
        MYclient.LOGIN(raw_input("Username: "),
                       raw_input("Password: "))
        
    except UNEXPECTED_RESPONSE:
        print "Incorrect login"
        sys.exit(1)
    
    MYclient.MODE()
    MYclient.TYPE('I')
    MYclient.STRU()

    MYclient.CWD('/')
    MYclient.MKD('test')
    MYclient.CWD('test')

    dest = 'Hassan_Prueba.py'
    MYclient.upload(dest, sys.argv[0])
    
    folder = MYclient.DIR()
    fsize = MYclient.SIZE(dest)
    ftime = MYclient.TIME(dest)

    MYclient.QUIT()

    if dest in folder:
        print "Success! '%s' uploaded to the folder.\n\n Size: %s BYTES\n Time: %s"%(dest,
                                                                               fsize,
                                                                               time.ctime(ftime))
    else:
        print "File did not succesfully upload."
