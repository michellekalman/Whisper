import socket

import yaml
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 2222

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
cipher_suite = Fernet(config['fernet_key'])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    while True:
        s.listen()
        conn, addr = s.accept()
        conn.settimeout(1)
        with conn:
            print(f"Connected by {addr}")
            all_data = b""
            while True:
                try:
                    data = conn.recv(1024)
                    all_data += data
                except socket.timeout:
                    break
                if not data:
                    break

            # decode data
            decrypted_data = cipher_suite.decrypt(all_data).decode("utf-8")
            print(f"Message from Client: {decrypted_data}")
