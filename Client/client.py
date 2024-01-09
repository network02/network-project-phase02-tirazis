import socket


def send_command(command, client_socket):
    client_socket.send(command.encode())
    response_ = client_socket.recv(1024).decode().strip()
    print("Server response:", response_)
    return response_


# Set up client socket
Host = '127.0.0.1'  # Change this to the IP address of your server
Port = 10021  # Make sure this matches the port your server is using

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Host, Port))
n = 0
while True:
    if n == 0:
        client.send('FIRST'.encode())
        response = client.recv(1024).decode()
        print(response)
    user_input = input(">> ")
    if user_input.split(' ')[0].upper().startswith('RETR')  :
        client.send(user_input.encode())
        response = client.recv(1024).decode()
        client.send('response'.encode())
        
        
        file_size_str = client.recv(1024)
        file_size = int(file_size_str)
        client.sendall(b'ACK')
        received_data = b''
        while len(received_data) < file_size:
            data = client.recv(1024)
            received_data += data


        with open('A-Cat.jpg', 'wb') as file:
            file.write(received_data)
        client.send('FINISH'.encode())
        res = client.recv(1024).decode()
        print(res)
          
        continue
    if user_input.split(' ')[0].upper().startswith('STOR') :
        client.send('STOR'.encode())
        file_name = user_input[5:]
        
        response = client.recv(1024).decode()
        with open(file_name, 'rb') as file:
            file_data = file.read()
        file_size_str = str(len(file_data))
        client.sendall(file_size_str.encode())
        response = client.recv(1024).decode()
        client.sendall(file_data)
        res = client.recv(1024).decode()
        print(res)
        continue
        
        
        


    if user_input.upper() == 'QUIT':
        client.send("QUIT\r\n".encode())
        break

    response = send_command(user_input + '\r\n', client)
    n += 1

client.close()
