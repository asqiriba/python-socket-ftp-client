#!/usr/bin/env python3

import cmd
import socket
import os
import mimetypes

EOL = '\r\n'
TEXT_FILETYPES = ['css', 'html', 'js', 'txt', 'htm', 'csv', 'bat', 'sh', 'php', 'py', 'pyw', 'bas', 'c']


class ClienteFTP(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'ftp > '
        self.intro = """
                * * * * * * * * * * * * * * * * * * * * * * *
                * Bienvenido al cliente de FTP por @federiz *
        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        * Introduzca 'help' para ver la lista de comandos disponibles.  *
        * Introduzca 'help comando' para ayuda sobre un comando.        *
        *****************************************************************
        """
        self.logged = False
        self.is_pasv = False
        self.sock = False
        self.pasv_socket = False

    def iniciar_socket(self):
        """Inicializa el socket para transmisión de comandos FTP"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def init_pasv_socket(self, connection):
        """Inicializa el socket para transmisión de datos FTP"""
        self.pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            connection = connection[connection.rindex('(') + 1:connection.rindex(')')]
        except ValueError:
            self.sock.recv(1024)
            self.do_pasv()
            return False

        parts = connection.split(',')
        host = parts[0] + '.' + parts[1] + '.' + parts[2] + '.' + parts[3]
        port = int(parts[4]) * 256 + int(parts[5])
        try:
            self.pasv_socket.connect((host, port))
            self.is_pasv = True
            return True
        except socket.gaierror:
            return False


    def recibir(self, pasv_mode=False):
        """Recibe 1Kb de datos por medio del socket PASV"""
        if pasv_mode:
            response = self.pasv_socket.recv(1024)
        else:
            response = self.sock.recv(1024)
        return response

    def dec_response(self, response):
        """Decodifica la cadena binaria de respuesta del servidor FTP"""
        return response.decode('ascii')

    def enviar(self, comando, pasv_mode=False):
        """Envia un comando o datos al servidor FTP."""
        try:
            if pasv_mode:
                self.pasv_socket.sendall((comando + EOL).encode('ascii'))
            else:
                self.sock.sendall((comando + EOL).encode('ascii'))
        except BrokenPipeError:
            print('Se ha perdido la conexion al servidor, intente conectarse nuevamente')

    def comando(self, comando, pasv_mode=False):
        """Ejecuta un comando en el servidor FTP"""
        if self.logged:
            self.enviar(comando, pasv_mode)
            respuesta = self.recibir(pasv_mode)
            return respuesta
        else:
            self.do_conectar('')

    def do_conectar(self, line):
        """
        Inicia la conexión a un servidor de FTP.
        Se le preguntarán los siguientes datos:
             Servidor:   Nombre del host del servidor FTP
             Puerto:     Puerto en que responde el servidor FTP (Por defecto es el puerto 21)
             Usuario:    Nombre de usuario (Anonymous por defecto)
             Contraseña: Contraseña del usuario autorizado
        """
        server = input('Servidor: ')
        port = input('Puerto [21]: ')
        user = input('Usuario [anonymous]: ')
        passwd = input('Contraseña: ')

        print('Conectando al servidor....' + EOL)

        if port == '':
            port = 21
        if user == '':
            user = 'anonymous'
            passwd = ''

        self.iniciar_socket()

        try:
            self.sock.connect((server, int(port)))
            respuesta = self.recibir()

            #Mostrar el mensaje de bienvenida del servidor
            print(self.dec_response(respuesta))

            self.enviar("USER " + user)

            respuesta = self.recibir()

            self.logged = False

            if "331 " in self.dec_response(respuesta):
                self.enviar("PASS " + passwd)
                respuesta = self.recibir()
                if "230 " in self.dec_response(respuesta):
                    self.logged = True

            if self.logged:
                print("Conexión exitosa. Bienvenido " + user)
                self.do_list(line)
            else:
                print('Usuario o contraseña inválidos.')
                self.cerrar_conexion()

        except ConnectionRefusedError:
            print("El servidor ha rechazado la conexión. Intente nuevamente.")
            self.do_salir
        except socket.gaierror:
            print("No se puede conectar al servidor. Intente nuevamente.")

    def do_pwd(self, line):
        """
        Imprime la ruta del directorio actual en el servidor FTP
        Ejemplo: ftp > pwd
                 >> 257 "/"
        """
        print(self.dec_response(self.comando('pwd')))

    def do_pasv(self):
        """
        Inicializa el socket para transmisión de datos FTP
        Ejemplo: ftp > pasv
                 >> 227 Entering Passive Mode (127,0,0,1,226,229).
        """
        r = self.dec_response(self.comando('pasv'))
        print(r)
        self.init_pasv_socket(r)

    def do_type(self, line):
        """
        Establece el tipo de transmisión de datos FTP
        Ejemplo: ftp > type I
                 >> 200 Type set to I.
        """
        print(self.dec_response(self.comando('type ' + line)))

    def do_list(self, line):
        """
        Presenta un listado del directorio actual del servidor FTP
        Ejemplo: ftp > list
                 >> 125 Data connection already open, starting transfer
                 >> 226 Transfer Complete.
                 >> Contenido de: "/"
                 >> drwxrwxr-x   7 user user            4096 May 02 03:53 directorio
                 >> drwxrwxr-x   7 user user              96 May 06 11:55 Hola.txt
        """
        self.do_pwd(line)
        self.do_type('I')
        cdir = self.dec_response(self.comando('pwd'))

        self.do_pasv()

        self.sock.sendall(('LIST' + '\r\n').encode('ascii'))
        r = self.sock.recv(1024)

        print(self.dec_response(r))

        pasv_resp = self.recibir(True)

        print('Contenido de: ' + cdir[4:])
        print(self.dec_response(pasv_resp))

        if not "226 " in self.dec_response(r):
            r = self.sock.recv(1024)
            print(self.dec_response(r))

        self.close_pasv()


    def close_pasv(self):
        """Cierra el socket de transmisión de datos PASV FTP"""
        self.pasv_socket.close()
        self.is_pasv = False

    def do_cwd(self, line):
        """Cambia el directorio activo en el servidor FTP"""
        print(self.dec_response(self.comando('cwd ' + line)))
        self.do_list(line)

    def do_mkd(self, line):
        """Crea un nuevo directorio en el servidor FTP"""
        print(self.dec_response(self.comando('mkd ' + line)))
        self.do_list(line)

    def do_size(self, line):
        """Obtiene el tamaño de un archivo en el servidor FTP"""
        size = self.get_filefize(line)
        print(size)

    def get_filefize(self, file):
        """Llama al comando para obtener el tamaño de un archivo en bytes del servidor FTP"""
        size = self.dec_response(self.comando('size ' + file))
        return size

    def do_cdup(self, line):
        """Cambia al directorio padre inmediato superior en el servidor FTP"""
        print(self.dec_response(self.comando('mcdup')))
        self.do_list(line)

    def do_mode(self, line):
        """Establece el modo de transferencia de datos"""
        print(self.dec_response(self.comando('mode ' + line)))

    def do_stru(self, line):
        """Establece la estructura de transmisión de datos"""
        print(self.dec_response(self.comando('stru ' + line)))

    def do_pwdx(self, line):
        """Imprime la ruta de directorios local actual"""
        print(os.getcwd())

    def do_chwdx(self, line):
        """Cambia la ruta actual de directorio local"""
        os.chdir(line)
        self.do_pwdx(line)

    def do_dirx(self, line):
        """Presenta un listado del contenido del directorio local actual"""
        if line == '':
            line = '.'
        files = os.listdir(line)
        for file in files:
            filetype = mimetypes.guess_type(file)
            stats = os.stat(os.path.join(line, file))
            if str(filetype[0]) == 'None':
                file = '[ ' + file + ' ]'
            print('{0:20} {1:20} {2:40}'.format(stats.st_size, str(filetype[0]), file))

    def do_dele(self, line):
        """Elmina el archivo especificado en el servidor FTP"""
        print(self.dec_response(self.comando('dele ' + line)))

    def do_chmod(self, line):
        """Cambia los permisos para el archivo seleccionado en el servidor FTP"""
        print(self.dec_response(self.comando('site chmod ' + line)))

    def do_noop(self, line):
        """Envía un comando noop al servidor FTP"""
        print(self.dec_response(self.comando('noop')))

    def do_retr(self, line):
        """Descarga el archivo seleccionado desde el servidor FTP"""
        if line[line.rindex('.') + 1:] in TEXT_FILETYPES:
            self.do_type('A')
            modo = ''
        else:
            self.do_type('I')
            modo = 'b'

        self.do_pasv()

        self.sock.sendall(('RETR ' + line + '\r\n').encode('ascii'))

        r = self.sock.recv(1024)
        r = self.sock.recv(1024)
        print(r.decode('ascii'))

        tamano = int(self.get_filefize(line)[4:])
        print("Recibiendo archivo " + line + " con un tamaño de " + str(tamano) + " bytes.")

        archivo = open(os.path.join(os.getcwd(), line), 'w' + modo)

        while tamano > 0:
            received = self.pasv_socket.recv(1024)
            tamano -= len(received)
            if modo == 'b':
                archivo.write(received)
            else:
                archivo.write(received.decode('UTF-8'))

        archivo.close()

        self.close_pasv()


    def do_stor(self, line):
        """Carga el archivo especificado al servidor FTP"""
        if line[line.rindex('.') + 1:] in TEXT_FILETYPES:
            self.do_type('A')
            modo = ''
        else:
            self.do_type('I')
            modo = 'b'

        self.do_pasv()

        self.sock.sendall(('STOR ' + line + '\r\n').encode('ascii'))

        archivo = open(line, 'r' + modo)
        if modo == 'b':
            self.pasv_socket.sendall(archivo.read())
        else:
            self.pasv_socket.sendall(archivo.read().encode('UTF-8'))

        archivo.close()
        self.pasv_socket.close()

        r = self.sock.recv(1024)
        print(r.decode('ascii'))

        r = self.sock.recv(1024)
        print(r.decode('ascii'))


    def cerrar_conexion(self):
        """
            Cierra un socket activo
        """
        try:
            self.sock.close()
        except AttributeError:
            pass


    def do_EOF(self, line):
        """"
            Cierra las conexiones y termina la ejecución del programa
        """
        self.cerrar_conexion()
        return True

    do_salir = do_EOF
    do_quit  = do_EOF


if __name__ == '__main__':
    """Loop principal del programa que inicializa el intérprete de comandos personalizados con cmd"""
    ClienteFTP().cmdloop()
