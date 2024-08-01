import socket
import yaml

from cryptography.fernet import Fernet

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1111  # The port used by the server

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
cipher_suite = Fernet(config['fernet_key'])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = b"It's sushi timeeeeeeeeee"
    encrypted_data = cipher_suite.encrypt(data)
    s.sendall(encrypted_data)
