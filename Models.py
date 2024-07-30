
class EnrichedData:
    def __init__(self, data, timestamp, client_ip, client_port, hashed_data):
        self.data = data
        self.timestamp = "timestamp: " + str(timestamp)
        self.client_ip = " client ip address: " + client_ip
        self.client_port = " client_port port: " + str(client_port)
        self.hashed_data = " hashed_data: " + str(hashed_data.digest())