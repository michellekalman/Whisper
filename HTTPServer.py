import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the length of the data
        content_length = int(self.headers['Content-Length'])
        # Read the data
        post_data = self.rfile.read(content_length)
        # Convert bytes to string
        post_data_str = post_data.decode('utf-8')
        # Parse JSON data
        data = json.loads(post_data_str)

        # Print the received data (for debugging purposes)
        print("Received data:")
        print(json.dumps(data, indent=4))

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'status': 'success'}
        self.wfile.write(json.dumps(response).encode('utf-8'))


if __name__ == '__main__':
    server_address = ('', 8080)  # Listen on all interfaces, port 8080
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Running mock HTTP server on port 8080...')
    httpd.serve_forever()
