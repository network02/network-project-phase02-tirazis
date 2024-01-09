import socket
import os
import threading
import time
from db_manager import *


class FTPthread(threading.Thread):
    def __init__(self, client, clientaddress, localip, dataport):
        self.log_messages = ''
        self.client = client
        self.client_address = clientaddress
        self.data_address = (localip, dataport)
        self.cwd = os.getcwd

        threading.Thread.__init__(self)

        self.conn = sqlite3.connect('users.db', check_same_thread=False)  # Connect to the database
        self.cursor = self.conn.cursor()
        self.report_conn = sqlite3.connect('user_actions.db', check_same_thread=False)
        self.report_cursor = self.report_conn.cursor()

    def run(self):
        # Sending the welcome message to the client
        cmd = self.client.recv(1024)
        if cmd.decode() == 'FIRST':
            welcome_message = "\n... < Welcome to the FTP server > ...\n(!) Available commands:\n"
            for command, description in commands_list:
                welcome_message += f"\t{command}-->\t{description}\n"
            self.client.send(welcome_message.encode())
        while True:
            try:
                cmd = self.client.recv(1024)
                str_cmd = cmd.decode().strip()
                user_str_cmds = str_cmd.split(' ')
                user_command = user_str_cmds[0].upper()
                username = user_str_cmds[1]
            except:
                print('USER QUIT')
                break

            # Handle USER-Login
            if user_command == 'LOGIN':
                try:
                    if user_str_cmds[1] == 'admin' and user_str_cmds[2] == 'admin':
                        self.client.send("230 Logged in successfully\r\n".encode())
                        self.switches(2, username)
                        break

                    password = user_str_cmds[2]
                    if authenticate_user(username, password):
                        # Log the action in the database
                        self.log_action(username, f"LOGIN")
                        self.client.send("230 Logged in successfully\r\n".encode())
                        print(f'(!) USER \"{username}\" logged-in to server')
                        self.switches(1, username)
                        break
                    else:
                        self.client.send("530 Login incorrect\r\n".encode())
                        continue
                except:
                    # Log the action in the database
                    self.log_action(username, f"QUIT")
                    print(f"(!) USER \"{username}\" leaved from server.")
                    break
                    # Handle SIGNUP
            elif user_command == 'SIGNUP':
                try:
                    username = user_str_cmds[1]
                    password = user_str_cmds[2]

                    create_user(username, password)
                    # Log the action in the database
                    self.log_action(username, f"SIGNUP")
                    self.client.send("201 User created successfully\r\n".encode())
                    print(f'(!) USER \"{username}\" Signed-up in server')
                except:
                    self.client.send("500 Syntax error, command unrecognized\r\n".encode())
                    break
            elif user_command == 'QUIT':
                self.client.send("221 Goodbye!\r\n".encode())
                break
            else:
                self.client.send("500 Syntax error, command unrecognized\r\n".encode())
        self.client.close()

    def switches(self, roll, username):
        while True:

            command = self.client.recv(1024).decode().strip()

            try:
                # Show the server items
                if command.startswith('LIST'):
                    pathname = ''
                    if len(command) > 4:
                        pathname = command[5:]
                    self.LIST(username, pathname)
                    continue
                # Download a file from server
                elif command.startswith('RETR'):
                    filename = command[5:]
                    if check_access(filename, username):
                        self.RETR(username, filename)
                        continue
                    else:
                        self.client.send("550 Permission denied\r\n".encode())
                    continue

                # Upload a file to server
                elif command.startswith('STOR'):
                    filename = command.split(' ')[1]
                    if check_access(filename, username):
                        self.RETR(filename)
                        continue
                    else:
                        self.client.send("550 Permission denied\r\n".encode())
                    continue

                # Delete a file in server
                elif command.startswith('DELE'):
                    filename = command[5:]
                    if check_access(filename, username):
                        self.DELE(username, filename)
                        continue
                    else:
                        self.client.send("550 Permission denied\r\n".encode())
                    continue
                # Create a new directory
                elif command.startswith('MKD'):
                    dir_name = command[4:]
                    dir_name = command.split(' ')[1]
                    self.MKD(username, dir_name)
                    continue
                # Returns the current working directory
                elif command.startswith('PWD'):
                    self.PWD(username)
                    continue
                #
                elif command.startswith('RMD'):
                    dir_name = command[4:]
                    if check_access(filename, username):
                        self.RMD(username, dir_name)
                        continue
                    else:
                        self.client.send("550 Permission denied\r\n".encode())
                    continue
                # Change directory in server side
                elif command.startswith('CWD'):
                    dir_name = command[4:]
                    self.CWD(dir_name)
                    continue
                elif command.startswith('CDUP'):
                    dir_name = command[4:]
                    self.CDUP()
                    continue
                elif command.startswith('REPORT') and roll == 2:
                    print('(!) Generating server-logs report for admin')
                    self.REPORT()
                    continue
                # Default unknown command
                else:
                    self.client.send('(!) Command unrecognized! Try a different command.'.encode())
                    continue
            except Exception as e:
                print(f"An error occurred: {e}")

    def __del__(self):
        try:
            self.conn.close()  # Close the database connection when the thread is destroyed
        except Exception as e:
            error_msg = f"An error occurred while closing the database connection: {e}"

    def LIST(self, username, pathname=''):

        try:
            if pathname:
                files = os.listdir(pathname)
            else:
                files = os.listdir()
            response = "150 Here are the files:\r\n"

            for file_name in files:
                file_info = os.stat(file_name)
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info.st_mtime))
                response += f"{mod_time} {file_name}\r\n"

            response += "\n226 Directory listing completed\r\n"
            # Log the action in the database
            self.log_action(username, f"LIST: {pathname}")
            self.client.send(response.encode())
        except FileNotFoundError:
            self.client.send(f"550 Path '{pathname}' not found\r\n".encode())
        except Exception as e:
            self.client.send(f"550 Failed to list directory '{pathname}': {str(e)}\r\n".encode())

    def RETR(self, username, filename):
        self.client.send("226 Transfer Began\r\n".encode())
        # Change this to the path of your JPEG file
        res = self.client.recv(1024).decode()
        print(res)

        with open(filename, 'rb') as file:
            file_data = file.read()

        # Send the file size first
        file_size = len(file_data)
        self.client.sendall(str(file_size).encode())

        self.client.recv(1024)
        self.client.sendall(file_data)

        self.client.recv(1024)
        # Log the action in the database
        self.log_action(username, f"RETR: {filename}")
        self.client.send("226 Transfer complete\r\n".encode())

    def STOR(self, filename):
        if not filename:
            self.client.send('501 Missing arguments <filename>.\r\n'.encode())
            return

        try:
            file_write = open(filename, 'wb')  # Open in binary mode for files
            while True:
                data = self.client.recv(1024)
                if not data:
                    break
                file_write.write(data)

            self.client.send('226 Transfer complete.\r\n'.encode())
        except IOError as e:
            print(f'ERROR: {str(self.client_address)}: {str(e)}')
            self.client.send('425 Error writing file.\r\n'.encode())
        except Exception as e:
            print(f'ERROR: {str(self.client_address)}: {str(e)}')
            self.client.send('451 Requested action aborted: local error in processing.\r\n'.encode())
        finally:
            try:
                file_write.close()
                self.client.close
            except Exception as e:
                print(f'ERROR: {str(self.client_address)}: {str(e)}')

    def DELE(self, username, filename):
        try:
            # Confirm deletion with the client
            self.client.send(f"250 Do you want to delete '{filename}'? (Y/N)\r\n".encode())
            confirmation = self.client.recv(1024).decode().strip().upper()

            if confirmation == 'Y':
                os.remove(filename)
                # Log the action in the database
                self.log_action(username, f"DELE: {filename}")
                self.client.send(f"250 File '{filename}' deleted successfully\r\n".encode())
            elif confirmation == 'N':
                self.client.send(f"250 Deletion of '{filename}' canceled\r\n".encode())
            else:
                self.client.send("550 Invalid choice. Deletion canceled\r\n".encode())

        except FileNotFoundError:
            self.client.send(f"550 File '{filename}' not found\r\n".encode())
        except Exception as e:
            self.client.send(f"550 Failed to delete file '{filename}': {str(e)}\r\n".encode())

    def MKD(self, username, dir_name):
        try:
            if os.path.isabs(dir_name):
                os.mkdir(dir_name)
                # Log the action in the database
                self.log_action(username, f"MKD: {dir_name}")
                self.client.send(f"257 '{dir_name}' directory created\r\n".encode())
            else:
                abs_path = os.path.join(self.cwd(), dir_name)
                os.mkdir(abs_path)
                # Log the action in the database
                self.log_action(username, f"MKD: {dir_name}")
                self.client.send(f"257 '{abs_path}' directory created\r\n".encode())
        except FileExistsError:
            self.client.send(f"550 Directory '{dir_name}' already exists\r\n".encode())
        except Exception as e:
            self.client.send(f"550 Failed to create directory '{dir_name}': {str(e)}\r\n".encode())

    def PWD(self, username):
        # Log the action in the database
        self.log_action(username, f"PWD")
        respond = os.getcwd()
        self.client.send(f"257 Current working directory is '{respond}'\r\n".encode())

    def RMD(self, username, dir_name):
        if os.path.isabs(dir_name):
            None
        else:
            abs_path = os.path.join(self.cwd(), dir_name)
        is_empty = not os.listdir(abs_path)
        try:
            if is_empty is True:
                os.rmdir(dir_name)
                # Log the action in the database
                self.log_action(username, f"RMD: {dir_name}")
                self.client.send(f"250 Directory '{dir_name}' deleted successfully\r\n".encode())
            else:
                os.removedirs(dir_name)
                # Log the action in the database
                self.log_action(username, f"RMD: {dir_name}")
                self.client.send(f"250 Directory '{dir_name}' deleted successfully\r\n".encode())
        except:
            self.client.send(f"550 Directory '{dir_name}' cant be removed\r\n".encode())

    # method to log actions in the database
    def log_action(self, username, action):
        try:
            self.report_cursor.execute("INSERT INTO user_actions (username, action) VALUES (?, ?)", (username, action))
            self.report_conn.commit()
        except Exception as e:
            print(f"Failed to log action: {e}")

    def REPORT(self):
        try:
            report = '..::Server-Report::..\n'
            # Perform database operations using the new connection and cursor
            self.report_cursor.execute("SELECT * FROM user_actions")
            actions = self.report_cursor.fetchall()
            for action in actions:
                report += f'{action}\n'  # Display actions or send them to the client as needed

            # Close the new connection and cursor
            self.report_cursor.close()
            self.report_conn.close()

            self.client.send(f"{report}\n257 Report generated successfully\r\n".encode())
        except Exception as e:
            self.client.send(f"550 Failed to generate report: {str(e)}\r\n".encode())


class FTP_server:
    def __init__(self):
        self.address = 'localhost'
        self.port = 10021
        self.dataport = 10020

    def start_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.address, self.port)

        try:
            print('(!) Creating data socket on', self.address, ':', self.port)
            self.sock.bind(server_address)
            self.sock.listen(5)
        except:
            print('Failed to create server on', self.address, ':', self.port)
            quit()

    def startt(self):
        conn = sqlite3.connect('users.db', check_same_thread=False)
        cursor = conn.cursor()
        # Users table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT
                )
            ''')
        # user_permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                accessibility TEXT,
                authorized_users TEXT
            )
        ''')

        report_conn = sqlite3.connect('user_actions.db', check_same_thread=False)
        report_cursor = report_conn.cursor()

        # user_actions table
        report_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        username TEXT,
                        action TEXT
                    )
                ''')

        print('...< FTP SERVER STARTED >...')
        self.start_socket()

        try:
            while True:
                client_socket, client_address = self.sock.accept()
                thread = FTPthread(client_socket, client_address, self.address, self.dataport)
                thread.daemon = True

                print('(!) New connection', )
                thread.start()
        except:
            print('closing')
            self.sock.close()
            quit()

    # Create the SQLite database and table if they don't exist


ftp_server = FTP_server()
ftp_server.startt()
