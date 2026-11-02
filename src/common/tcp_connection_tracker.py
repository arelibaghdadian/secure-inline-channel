
from scapy.all import IP, TCP

from src.common.connection_utils import create_connection_id


class TCPConnectionTracker:

    def __init__(self):
        self.connections = {}

    def process_packet(self, packet):

        if IP not in packet or TCP not in packet:
            return None

        ip = packet[IP]
        tcp = packet[TCP]

        source = (ip.src, tcp.sport)
        destination = (ip.dst, tcp.dport)

        # Detect the initial SYN from the client
        if tcp.flags & 0x02 and not tcp.flags & 0x10:

            connection = {
                "client_ip": ip.src,
                "client_port": tcp.sport,
                "server_ip": ip.dst,
                "server_port": tcp.dport,
                "client_isn": tcp.seq,
                "server_isn": None
            }

            self.connections[(source, destination)] = connection

            print("TCP SYN detected")
            print("Client ISN:", tcp.seq)

            return None

        # Detect SYN-ACK from the server
        if tcp.flags & 0x12 == 0x12:

            connection_key = (destination, source)
            connection = self.connections.get(connection_key)

            if connection is None:
                return None

            connection["server_isn"] = tcp.seq

            connection_id = create_connection_id(
                connection["client_ip"],
                connection["client_port"],
                connection["server_ip"],
                connection["server_port"],
                connection["client_isn"],
                connection["server_isn"]
            )

            connection["connection_id"] = connection_id

            print("TCP SYN-ACK detected")
            print("Server ISN:", tcp.seq)
            print("Connection ID:", connection_id.hex())

            return connection_id

        return None
