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
        response = client.recv(1024).decode().strip()
        print(response)
    user_input = input(">> ")

    if user_input.upper() == 'QUIT':
        client.send("QUIT\r\n".encode())
        break

    response = send_command(user_input + '\r\n', client)
    n += 1

client.close()
