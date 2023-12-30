import socket


def send_command(command, client_socket):
    client_socket.send(command.encode())
    response_ = client_socket.recv(1024).decode().strip()
    print("Server response:", response_)
    return response_


# Set up client socket
Host = 'localhost'
Port = 8081
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Host, Port))
while True:
    user_input = input("Enter command: ")

    if user_input.upper() == 'QUIT':
        client.send("QUIT\r\n".encode())
        break

    response = send_command(user_input + '\r\n', client)

client.close()
