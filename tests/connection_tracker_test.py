from scapy.all import IP, TCP

from src.common.tcp_connection_tracker import TCPConnectionTracker
from src.common.connection_utils import create_connection_id


# Create a tracker
tracker = TCPConnectionTracker()


# Simulate the client's SYN packet
syn_packet = (
    IP(src="10.0.1.2", dst="10.0.3.2") /
    TCP(sport=50122, dport=9000, flags="S", seq=1000)
)

print("Testing client SYN...")
tracker.process_packet(syn_packet)


# Simulate the server's SYN-ACK packet
syn_ack_packet = (
    IP(src="10.0.3.2", dst="10.0.1.2") /
    TCP(sport=9000, dport=50122, flags="SA", seq=2000, ack=1001)
)

print("\nTesting server SYN-ACK...")
connection_id = tracker.process_packet(syn_ack_packet)


# Verify the connection ID
expected_id = create_connection_id(
    "10.0.1.2", 50122,
    "10.0.3.2", 9000,
    1000, 2000
)

print("\nConnection ID generated:", connection_id is not None)
print("Connection ID matches:", connection_id == expected_id)
