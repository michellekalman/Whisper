import datetime
import hashlib
import socket
from concurrent.futures import ThreadPoolExecutor

import requests as requests
import yaml
from cryptography.fernet import Fernet

from Models import EnrichedData
from Utils import tcp_enrich_data, http_enrich_data


class Whisper:
    def __init__(self):
        self.listening_port = config['listening_port']
        self.ip_binding_address = config["ip_binding_address"]
        self.socket_timeout = config['socket_timeout']
        self.maximum_thread_number = config['maximum_thread_number']
        self.key = config['fernet_key']
        self.server_ip = config['target_server_details']['server_ip']
        self.server_port = config['target_server_details']['server_port']
        self.protocol = config['target_server_details']['protocol']
        self.http_url = config['target_server_details']['http_url']

    def _receive_data(self, conn, client_addr):
        conn.settimeout(self.socket_timeout)
        print(f"Connected by {client_addr}")
        all_data = b""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                all_data += data
        except socket.timeout:
            pass
        finally:
            conn.close()

        if all_data:
            decrypted_data = cipher_suite.decrypt(all_data)
            enriched_data = EnrichedData(
                data=decrypted_data,
                timestamp=datetime.datetime.now(),
                client_ip=client_addr[0],
                client_port=client_addr[1],
                hashed_data=hashlib.md5(decrypted_data)
            )
            return enriched_data
        return None

    def __transfer_http_data(self, enriched_data):
        encrypted_data = Fernet(self.key).encrypt(enriched_data['data'])
        enriched_data['data'] = encrypted_data.decode('utf-8')
        response = requests.post(self.http_url, json=enriched_data)
        return response.status_code

    def __transfer_tcp_data(self, enriched_data):
        encrypted_data = Fernet(self.key).encrypt(enriched_data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            return s.sendall(encrypted_data)

    def _transfer_data(self, enriched_data):
        if self.protocol == "HTTP":
            http_enriched_data = http_enrich_data(enriched_data)
            return self.__transfer_http_data(http_enriched_data)

        if self.protocol == "TCP":
            tcp_enriched_data = tcp_enrich_data(enriched_data)
            return self.__transfer_tcp_data(tcp_enriched_data)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip_binding_address, self.listening_port))
            s.listen()
            print(f"Server listening on {self.ip_binding_address}:{self.listening_port}")

            # max_workers parameter specifies the maximum number of threads that can be used simultaneously
            with ThreadPoolExecutor(max_workers=10) as executor:
                while True:
                    conn, client_addr = s.accept()
                    print(f"Accepted connection from {client_addr}")
                    # For each new connection, it accepts the connection and submits the handle_new_client task to
                    # handle the new client
                    executor.submit(self._handle_new_client, conn, client_addr)

    def _handle_new_client(self, conn, client_addr):
        enriched_data = self._receive_data(conn, client_addr)
        if enriched_data:
            res = self._transfer_data(enriched_data)
            print(f"Data sent with status code: {res}")


if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    cipher_suite = Fernet(config['fernet_key'])
    whisper = Whisper()
    whisper.start_server()
