
class EnrichedData:
    def __init__(self, data, timestamp, client_ip, client_port, hashed_data):
        self.data = data
        self.timestamp = timestamp
        self.client_ip = client_ip
        self.client_port = client_port
        self.hashed_data = hashed_data.digest()
