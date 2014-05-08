FTP

Watch it work: https://asciinema.org/a/9348
===



FTP in Python using sockets.






client7.py

FTP Client Class

----------------



This class consists of the following functions ...

.connect       connect to the host
.
.think         output a thought to the console (debugging)
.
.do_nothing    check for a connection.

.upload        upload a file by its name and contents
.
.LOGIN         login to the FTP with a username and password
.
.DIR           get a list of files
.
.SIZE          get the size of a file in bytes.

.CDUP          change to parent directory.

.CWD           change the current working directory
.
.MKD           create a new folder.

.MODE          set the transfer mode.

.TYPE          set the type of file to be transferred.

.STRU          set the file structure for transfer.

.PASV          a passive connection will have the data
 transfer port open.
.QUIT          close session and connections.



@Federiz
		
		*client7.py only works on Python2.2 or below.











clienteFedTP.py

FTP Client Class

----------------



This class consist of the following functions ...

.do_conectar	Connect to an FTP server.

.do_pwd		Print the present working directory of the FTP server.

.do_pwdx

.do_pasv	Passive connection.

.do_type	Sets type of file to be transferred.

.do_list	Lists PWD of the FTP server.

.do_cwd		Changes active working directory.

.do_mkd		Makes a new directory.

.do_size	Get size of a file in the FTP server.

.get_filefize	Calls the command to get file size in bytes.

.do_cdup	cd ..

.do_mode	Sets transfer mode.

.do_stru	Sets data transmission structure.

.do_stor	Loads file to the FTP server.

.do_chwdx	Changes active directory path.

.do_dirx	Lists content of pwd.

.do_dele	Deletes specific file.

.do_chmod	chmod to a selected file.

.do_noop	Assembly code for no-operation.

.do_retr	Downloads selected file from server.

.do_EOF		Ends connection and execution of the program.



@Federiz
		
		*clienteFedTP.py only works in Python3 or above.









FTP
Watch it work: https://asciinema.org/a/9348
(To be read in terminal.)
===

FTP in Python using sockets.


client7.py
FTP Client Class
----------------

This class consists of the following functions ...
.connect       connect to the host.
.think         output a thought to the console (debugging).
.do_nothing    check for a connection.
.upload        upload a file by its name and contents.
.LOGIN         login to the FTP with a username and password.
.DIR           get a list of files.
.SIZE          get the size of a file in bytes.
.CDUP          change to parent directory.
.CWD           change the current working directory.
.MKD           create a new folder.
.MODE          set the transfer mode.
.TYPE          set the type of file to be transferred.
.STRU          set the file structure for transfer.
.PASV          a passive connection will have the data.
               transfer port open on the server s side.
.QUIT          close session and connections.

@Federiz
		*client7.py only works on Python2.2 or below.





clienteFedTP.py
FTP Client Class
----------------

This class consist of the following functions ...
.do_conectar	Connect to an FTP server.
.do_pwd		Print the present working directory of the FTP server.
.do_pwdx
.do_pasv	Passive connection.
.do_type	Sets type of file to be transferred.
.do_list	Lists PWD of the FTP server.
.do_cwd		Changes active working directory.
.do_mkd		Makes a new directory.
.do_size	Get size of a file in the FTP server.
.get_filefize	Calls the command to get file size in bytes.
.do_cdup	cd ..
.do_mode	Sets transfer mode.
.do_stru	Sets data transmission structure.
.do_stor	Loads file to the FTP server.
.do_chwdx	Changes active directory path.
.do_dirx	Lists content of pwd.
.do_dele	Deletes specific file.
.do_chmod	chmod to a selected file.
.do_noop	Assembly code for no-operation.
.do_retr	Downloads selected file from server.
.do_EOF		Ends connection and execution of the program.

@Federiz
		*clienteFedTP.py only works in Python3 or above.
