import socket

# Sample user data
users = {
    'user1': {'username': 'Mehdi', 'password': '1234'},
    'user2': {'username': 'Bob', 'password': '25'},
    'user3': {'username': 'John', 'password': '35'},
}


def handle_USER(client_socket):
    while True:
        # Receive initial message from client
        data = client_socket.recv(1024).decode()
        print("Received:", data)

        # Check if the received message is 'USER username'
        if data.startswith("USER"):
            received_parts = data.split(" ")
            if len(received_parts) == 2:
                _, received_username = received_parts
                received_username = received_username.strip()  # Remove extra spaces
            user_found = False
            for user, info in users.items():
                if info['username'] == received_username:
                    user_found = True
                    client_socket.send("331 Enter password\r\n".encode())
                    password_attempt = client_socket.recv(1024).decode().strip()
                    print("Received:", password_attempt)
                    if password_attempt == f"PASS {info['password']}":
                        client_socket.send("230 Logged in successfully\r\n".encode())
                        # --- Here the server can respond to further commands from the client ---

                        break
                    else:
                        client_socket.send("530 Login incorrect\r\n".encode())
                    break

            if not user_found:
                client_socket.send("530 User not found\r\n".encode())
        elif data.strip().upper() == "QUIT":
            client_socket.send("221 Goodbye!\r\n".encode())
            break
        else:
            client_socket.send("500 Syntax error, command unrecognized\r\n".encode())

    client_socket.close()


def main():
    # Set up server socket
    host = 'localhost'
    port = 8081
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server is listening on http://{host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_USER(client_socket)
        client_socket.close()


if __name__ == '__main__':
    main()
