import datetime
import hashlib
import os
import shutil
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

import requests as requests
import yaml
from cryptography.fernet import Fernet

from Models import EnrichedData
from Utils import tcp_enrich_data, http_enrich_data, create_self_destruct_log_msg

SUCCESS_CODE = 200
HTTP = "HTTP"
TCP = "TCP"


class Whisper:
    def __init__(self):
        self.listening_port = config['listening_port']
        self.ip_binding_address = config["ip_binding_address"]
        self.socket_timeout = config['socket_timeout']
        self.maximum_thread_number = config['maximum_thread_number']
        self.key = config['fernet_key']
        self.self_destruction_message = config['self_destruction_message']
        self.self_destruction_client_ip = config['self_destruction_client_ip']
        self.data_files = config['data_files']
        self.data_dirs = config['data_dirs']
        self.server_ip = config['target_server_details']['server_ip']
        self.server_port = config['target_server_details']['server_port']
        self.protocol = config['target_server_details']['protocol']
        self.http_url = config['target_server_details']['http_url']
        self.active_connections = []
        self.self_destruction_flag = threading.Event()

    def _receive_data(self, conn, client_addr):
        self.active_connections.append(conn)
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
            self.active_connections.remove(conn)

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

    def __http_send_self_destruction_log(self, client_ip):
        log_message = {
            "data": f"{create_self_destruct_log_msg(client_ip)}",
        }
        encrypted_data = Fernet(self.key).encrypt(log_message['data'].encode("utf-8"))
        log_message["data"] = encrypted_data.decode("utf-8")
        try:
            response = requests.post(self.http_url, json=log_message)
            if response.status_code == SUCCESS_CODE:
                print("Self-destruction log sent successfully.")
            else:
                print(f"Failed to send self-destruction log, status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending self-destruction log: {e}")

    def __tcp_send_self_destruction_log(self, client_ip):
        log_message = create_self_destruct_log_msg(client_ip)
        encrypted_data = Fernet(self.key).encrypt(log_message.encode("utf-8"))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            return s.sendall(encrypted_data)

    def _send_self_destruction_log(self, client_ip):
        if self.protocol == HTTP:
            return self.__http_send_self_destruction_log(client_ip)

        if self.protocol == TCP:
            return self.__tcp_send_self_destruction_log(client_ip)

    def _check_self_destruction(self, enriched_data):
        if (enriched_data.client_ip == self.self_destruction_client_ip and
                enriched_data.data.decode('utf-8') == self.self_destruction_message):
            print(f"Self destruction triggered!")
            enriched_data.data = b''
            self.self_destruction_flag.set()
            self._send_self_destruction_log(enriched_data.client_ip)
            return True
        return False

    def __transfer_http_data(self, enriched_data):
        encrypted_data = Fernet(self.key).encrypt(enriched_data['data'])
        enriched_data['data'] = encrypted_data.decode('utf-8')
        try:
            requests.post(self.http_url, json=enriched_data)

        except Exception as e:
            # The server doesn't reply to the request
            pass

    def __transfer_tcp_data(self, enriched_data):
        encrypted_data = Fernet(self.key).encrypt(enriched_data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            s.sendall(encrypted_data)

    def _transfer_data(self, enriched_data):
        if self.protocol == HTTP:
            http_enriched_data = http_enrich_data(enriched_data)
            self.__transfer_http_data(http_enriched_data)

        if self.protocol == TCP:
            tcp_enriched_data = tcp_enrich_data(enriched_data)
            self.__transfer_tcp_data(tcp_enriched_data)

    def _delete_data(self):
        for file_path in self.data_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                else:
                    print(f"File not found: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        for dir_path in self.data_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
                else:
                    print(f"Directory not found: {dir_path}")
            except Exception as e:
                print(f"Error deleting directory {dir_path}: {e}")

    def start_server(self):
        # max_workers parameter specifies the maximum number of threads that can be used simultaneously
        with ThreadPoolExecutor(max_workers=10) as executor:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.ip_binding_address, self.listening_port))
                s.listen()
                print(f"Server listening on {self.ip_binding_address}:{self.listening_port}")

                while not self.self_destruction_flag.is_set():
                    try:
                        conn, client_addr = s.accept()
                        print(f"Accepted connection from {client_addr}")
                        # For each new connection, it accepts the connection and submits the handle_new_client task to
                        # handle the new client
                        executor.submit(self._handle_new_client, conn, client_addr)
                    except socket.timeout:
                        continue

            # Stop accepting new connections
            s.close()
            print("Stopped accepting new connections")

            # Close all active connections
            for conn in self.active_connections:
                conn.close()
            print("Closed all active connections")

            self._delete_data()
            print("Finished deleting all the data")

    def _handle_new_client(self, conn, client_addr):
        enriched_data = self._receive_data(conn, client_addr)
        if enriched_data:
            if self._check_self_destruction(enriched_data):
                print(f"Self distracting!")
            else:
                self._transfer_data(enriched_data)


if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    cipher_suite = Fernet(config['fernet_key'])
    whisper = Whisper()
    whisper.start_server()
