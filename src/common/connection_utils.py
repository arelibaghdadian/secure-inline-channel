import hashlib


def create_connection_id(
    client_ip,
    client_port,
    server_ip,
    server_port,
    client_isn,
    server_isn
):
    connection_info = (
        f"{client_ip}:{client_port}-"
        f"{server_ip}:{server_port}-"
        f"{client_isn}-{server_isn}"
    )

    connection_id = hashlib.sha256(
        connection_info.encode()
    ).digest()

    return connection_id
