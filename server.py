import socket
import os
import threading
import time
users = {
    'user1': {'username': 'Mehdi', 'password': '1234'},
    'user2': {'username': 'Bob', 'password': '25'},
    'user3': {'username': 'John', 'password': '35'},
}

class FTPthread(threading.Thread):
    def __init__(self, client, clientaddress, localip, dataport):
        self.client = client
        self.client_address = clientaddress
        self.data_address = (localip, dataport)
        self.cwd = os.getcwd
        threading.Thread.__init__(self)
    

    def run(self):
        print('connected : ', self.client_address)     
        while True:   
            cmd = self.client.recv(1024)
            str_cmd = cmd.decode().strip()
            user_str_cmds = str_cmd.split(' ')
            user_command = user_str_cmds[0].upper()
            username = user_str_cmds[1]
            print(user_command, ' : ', username)
            if user_command == 'USER':
                for user, info in users.items():
                    if info['username'] == username:
                        self.client.send("331 Enter password\r\n".encode())
                        try:
                            data = self.client.recv(1024).decode().strip()
                            print("Received:", data)
                            user_str_cmds = data.split(' ')
                            user_command = user_str_cmds[0].upper()
                            password = user_str_cmds[1]
                            if info['password'] == password:
                                self.client.send("230 Logged in successfully\r\n".encode())
                                self.switches()
                                break
                            else:
                                self.client.send("530 Login incorrect\r\n".encode())   
                            break
                        except:
                            self.client.send("500 Syntax error, command unrecognized\r\n".encode())
                            continue
                    else:
                        self.client.send("530 User not found\r\n".encode()) 
            elif user_command == 'QUIT':
                self.client.send("221 Goodbye!\r\n".encode())
                break
            else:
                self.client.send("500 Syntax error, command unrecognized\r\n".encode())
        self.client.close()

    def switches(self):
        self.client.send('aaaaaaaaaaaaaaaa'.encode())
        command = self.client.recv(1024).decode().strip().upper()
        match command:
            case 'LIST':
                self.listt()
                

    def listt(self):
        self.client.send('LIST ... .. . '.encode())        







                    

            
            
    

class FTPserv:
    def __init__(self, port, dataport):
        self.address = '0.0.0.0'
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
            quit()




port = input('port: ')
data_port = input('data port: ')
ftpserver = FTPserv(port, data_port)
print(ftpserver.address)
ftpserver.startt()
