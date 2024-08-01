import datetime


def tcp_enrich_data(enriched_data):
    combined_data = ("timestamp: " + str(enriched_data.timestamp)).encode("utf-8") + \
                    (" client ip address: " + enriched_data.client_ip).encode("utf-8") + \
                    (" client_port port: " + str(enriched_data.client_port)).encode("utf-8") + \
                    (" hashed_data: " + str(enriched_data.hashed_data)).encode("utf-8") + \
                    enriched_data.data
    return combined_data


def http_enrich_data(enriched_data):
    header = {
        'timestamp': ("timestamp: " + str(enriched_data.timestamp)),
        'client_ip': (" client ip address: " + enriched_data.client_ip),
        'client_port': (" client_port port: " + str(enriched_data.client_port)),
        'md5_hash': (" hashed_data: " + str(enriched_data.hashed_data))
    }
    enriched_data = {
        'header': header,
        'data': enriched_data.data
    }
    return enriched_data


def create_self_destruct_log_msg(client_ip):
    return f"Self destruction triggered with {client_ip} client ip at {datetime.datetime.now().isoformat()}"
