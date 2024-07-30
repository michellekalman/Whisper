import socket

HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    while True:
        s.listen()
        conn, addr = s.accept()
        conn.settimeout(1)
        with conn:
            print(f"Connected by {addr}")
            all_data = ""
            while True:
                try:
                    data = conn.recv(1024)
                    all_data += str(data)
                except socket.timeout:
                    break
                if not data:
                    break
            print(all_data)

