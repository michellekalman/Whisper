import datetime
import hashlib
import socket

import requests as requests
import yaml

from Utils import tcp_enrich_data, http_enrich_data


class EnrichedData:
    def __init__(self, data, timestamp, client_ip, client_port, hashed_data):
        self.data = data
        self.timestamp = "timestamp: " + str(timestamp)
        self.client_ip = " client ip address: " + client_ip
        self.client_port = " client_port port: " + str(client_port)
        self.hashed_data = " hashed_data: " + str(hashed_data.digest())


class Whisper:
    def __init__(self):
        self.listening_port = config['listening_port']
        self.ip_binding_address = config["ip_binding_address"]
        self.server_ip = config['target_server_details']['server_ip']
        self.server_port = config['target_server_details']['server_port']
        self.protocol = config['target_server_details']['protocol']
        self.http_url = config['target_server_details']['http_url']
        self.socket_timeout = config.get('socket_timeout', 10)  # Set default timeout to 10 seconds if not provided

    def receive_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip_binding_address, self.listening_port))
            s.listen()
            conn, client_addr = s.accept()
            conn.settimeout(self.socket_timeout)
            with conn:
                print(f"Connected by {client_addr}")
                data = b""
                while True:
                    try:
                        data += conn.recv(1024)
                    except socket.timeout:
                        break

                    if not data:
                        break

                return EnrichedData(data=data, timestamp=datetime.datetime.now(), client_ip=client_addr[0],
                                    client_port=client_addr[1], hashed_data=hashlib.md5(data))

    def transfer_http_data(self, enriched_data):
        response = requests.post(self.http_url, json=enriched_data)
        return response.status_code

    def transfer_tcp_data(self, combined_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            return s.sendall(combined_data)

    def transfer_data(self, enriched_data):
        if self.protocol == "HTTP":
            http_enriched_data = http_enrich_data(enriched_data)
            return self.transfer_http_data(http_enriched_data)

        if self.protocol == "TCP":
            tcp_enriched_data = tcp_enrich_data(enriched_data)
            return self.transfer_tcp_data(tcp_enriched_data)


if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    whisper = Whisper()
    while True:
        print(1)
        general_enriched_data = whisper.receive_data()
        res = whisper.transfer_data(general_enriched_data)
        print(f"Data sent with status code: {res}")
