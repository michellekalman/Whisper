import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml
from cryptography.fernet import Fernet


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the length of the data
        content_length = int(self.headers['Content-Length'])
        # Read the data
        post_data = self.rfile.read(content_length)
        # Convert bytes to string
        post_data_str = post_data.decode('utf-8')
        # Parse JSON data
        packet = json.loads(post_data_str)
        print(f"Message from client:")
        print(f"Header : {str(packet['header'])}")
        decrypted_data = cipher_suite.decrypt(packet['data']).decode("utf-8")
        print(f"Data from Client: {decrypted_data}")


if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    cipher_suite = Fernet(config['fernet_key'])
    server_address = ('', 8080)  # Listen on all interfaces, port 8080
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Running mock HTTP server on port 8080...')
    httpd.serve_forever()
