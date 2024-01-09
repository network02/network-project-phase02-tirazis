import sqlite3

commands_list = [
    ("LOGIN\t", "Login to the FTP server: LOGIN <username> <password>"),
    ("SIGNUP\t", "Create a new user: SIGNUP <username> <password>"),
    ("LIST\t", "List contents of a directory: LIST <path>"),
    ("RETR\t", "Retrieve a file: RETR <filename>"),
    ("STOR\t", "Store a file: STOR <filename>"),
    ("DELE\t", "Delete a file: DELE <filename>"),
    ("MKD\t", "Make a directory: MKD <directory name>"),
    ("RMD\t", "Remove a directory: RMD <directory name>"),
    ("PWD\t", "Print working directory: PWD"),
    ("CWD\t", "Change working directory: CWD <directory name>"),
    ("CDUP\t", "Change to the parent directory: CDUP"),
    ("QUIT\t", "Quit the FTP session: QUIT"),
    ("REPORT\t", "(Only for admin) Generate a server report: REPORT")
]


# Function to add a new user to the database
def create_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()


# Function to handle user authentication against the database
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    conn.close()

    if result and result[0] == password:
        return True
    else:
        return False


def check_access(filename, username):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT accessibility, authorized_users FROM user_permissions WHERE filename=?", (filename,))
        access_data = cursor.fetchone()

        if access_data:
            accessibility, authorized_users = access_data
            if accessibility == 'public':
                return True
            elif accessibility == 'private' and authorized_users:
                authorized_users = authorized_users.split(',')  # Convert to list
                if username in authorized_users:
                    return True

        return False

    except Exception as e:
        error_msg = f"An error occurred while checking access: {e}"
        print(error_msg)
        return False
