import socket
import os
import sys
import threading
import time


class FTPthread(threading.Thread):
    def __init__(self, client, clientaddress, localip, dataport):
        self.client = client
        self.client_address = clientaddress
        self.data_address = (localip, dataport)

        threading.Thread.__init__(self)
    

class FTPserv:
    def __init__(self, port, dataport):
        self.address = '127.0.0.1'
        self.port = int(port)
        self.dataport = int(dataport)
        
    def startsockettt(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.address, self.port)

        try:
            print ('Creating data socket on', self.address, ':', self.port, '...')
            self.sock.bind(server_address)
            self.sock.listen(5)
            print ('Server is up. Listening to', self.address, ':', self.port)
        except:
            print ('Failed to create server on', self.address, ':', self.port)
            quit()
    def startt(self):
        self.startsockettt()

        try:
            while True:
                print('waiting...')
                client_socket, client_address = self.sock.accept()
                thread = FTPthread(client_socket, client_address, self.address, self.dataport)
                thread.daemon = True
                print('888')
                thread.start()
        except:
            print('closing')
            self.sock.close()
            quit




port = input('port: ')
data_port = input('data port: ')
ftpserver = FTPserv(port, data_port)
print(ftpserver.address)
ftpserver.startt()
