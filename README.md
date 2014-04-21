FTP
===

FTP in Python3 using sockets.

FTP Client Class
----------------

This class consists of the following functions ...
.connect       connect to the host
.think         output a thought to the console (debugging)
.do_nothing    check for a connection
.upload        upload a file by its name and contents
.LOGIN         login to the FTP with a username and password
.DIR           get a list of files
.SIZE          get the size of a file in bytes
.CDUP          change to parent directory
.CWD           change the current working directory
.MKD           create a new folder
.MODE          set the transfer mode
.TYPE          set the type of file to be transferred
.STRU          set the file structure for transfer
.PASV          a passive connection will have the data
               transfer port open on the server' s side
.QUIT          close session and connections.
@Federiz
