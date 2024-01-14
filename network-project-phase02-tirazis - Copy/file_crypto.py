from cryptography.fernet import Fernet


# Generate a key and save it to a file
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)


# Load the key from the file
def load_key():
    return open("key.key", "rb").read()


# Encrypt a file
def encrypt_file(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(filename, "wb") as file:
        file.write(encrypted_data)


# Decrypt a file
def decrypt_file(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    decrypted_data = f.decrypt(file_data)
    with open(filename, "wb") as file:
        file.write(decrypted_data)
