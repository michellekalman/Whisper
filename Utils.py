def tcp_enrich_data(enriched_data):
    combined_data = enriched_data.timestamp.encode("utf-8") + \
                    enriched_data.client_ip.encode("utf-8") + \
                    enriched_data.client_port.encode("utf-8") + \
                    enriched_data.hashed_data.encode("utf-8") + \
                    enriched_data.data
    return combined_data


def http_enrich_data(enriched_data):
    header = {
        'timestamp': enriched_data.timestamp,
        'client_ip': enriched_data.client_ip,
        'client_port': enriched_data.client_port,
        'md5_hash': enriched_data.hashed_data
    }
    enriched_data = {
        'header': header,
        'data': enriched_data.data.decode('utf-8')
    }
    return enriched_data
