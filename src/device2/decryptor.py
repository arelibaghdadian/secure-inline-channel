
from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, Raw
from cryptography.exceptions import InvalidTag

from src.common.tcp_connection_tracker import TCPConnectionTracker
from src.common.crypto_utils import derive_connection_key
from src.common.packet_crypto import encrypt_tcp_payload, decrypt_tcp_payload
from src.common.retransmission_cache import RetransmissionCache


# Load Device2's session key
with open("/tmp/device2-session.key", "rb") as file:
    session_key = file.read()


tracker = TCPConnectionTracker()
cache = RetransmissionCache()


def process_packet(packet):

    data = packet.get_payload()
    ip_packet = IP(data)

    if IP not in ip_packet or TCP not in ip_packet:
        packet.accept()
        return

    tcp_packet = ip_packet[TCP]

    # Observe the TCP handshake
    tracker.process_packet(ip_packet)

    # Determine packet direction
    if ip_packet.src == "10.0.1.2" and ip_packet.dst == "10.0.3.2":
        direction = b"PC1-to-PC2"
        is_reverse = False

        connection_key = (
            (ip_packet.src, tcp_packet.sport),
            (ip_packet.dst, tcp_packet.dport)
        )

    elif ip_packet.src == "10.0.3.2" and ip_packet.dst == "10.0.1.2":
        direction = b"PC2-to-PC1"
        is_reverse = True

        connection_key = (
            (ip_packet.dst, tcp_packet.dport),
            (ip_packet.src, tcp_packet.sport)
        )

    else:
        packet.accept()
        return

    original_payload = bytes(tcp_packet.payload)

    if not original_payload:
        packet.accept()
        return

    # Find the established connection
    connection = tracker.connections.get(connection_key)

    if connection is None or connection["server_isn"] is None:
        print("Connection not established. Packet rejected.")
        packet.drop()
        return

    connection_id = connection["connection_id"]

    # Derive the directional key
    connection_key_bytes = derive_connection_key(
        session_key,
        connection_id,
        direction
    )

    try:

        if is_reverse:
            # Encrypt PC2 -> PC1 traffic
            processed_payload = encrypt_tcp_payload(
                connection_key_bytes,
                cache,
                connection_id,
                direction,
                tcp_packet.seq,
                original_payload
            )

            print("\n--- Device2: TCP Payload Encrypted ---")

        else:
            # Decrypt PC1 -> PC2 traffic
            processed_payload = decrypt_tcp_payload(
                connection_key_bytes,
                tcp_packet.seq,
                original_payload
            )

            print("\n--- Device2: TCP Payload Decrypted ---")

    except InvalidTag:
        print("Authentication failed! Packet rejected.")
        packet.drop()
        return

    except (ValueError, RuntimeError) as error:
        print("Packet processing failed:", error)
        packet.drop()
        return

    # Replace the TCP payload
    tcp_packet.remove_payload()
    tcp_packet.add_payload(Raw(load=processed_payload))

    # Recalculate IP/TCP lengths and checksums
    del ip_packet.len
    del ip_packet.chksum
    del tcp_packet.chksum

    packet.set_payload(bytes(ip_packet))

    print("Connection ID:", connection_id.hex())
    print("Original payload length:", len(original_payload))
    print("Processed payload length:", len(processed_payload))

    packet.accept()


queue = NetfilterQueue()
queue.bind(1, process_packet)

print("Device2 bidirectional processor started.")
print("Waiting for TCP packets...")

try:
    queue.run()

except KeyboardInterrupt:
    print("\nStopping Device2 processor.")
    queue.unbind()
