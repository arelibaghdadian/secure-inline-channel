from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, Raw


def process_packet(packet):
    data = packet.get_payload()
    ip_packet = IP(data)

    if IP in ip_packet and TCP in ip_packet:
        tcp_packet = ip_packet[TCP]
        original_payload = bytes(tcp_packet.payload)

        if original_payload:
            print("\n--- TCP Packet ---")
            print("Original payload:", original_payload)

            # Create a replacement with the same length
            new_payload = b"X" * len(original_payload)

            tcp_packet.remove_payload()
            tcp_packet.add_payload(Raw(load=new_payload))

            # Recalculate packet lengths and checksums
            del ip_packet.len
            del ip_packet.chksum
            del tcp_packet.chksum

            packet.set_payload(bytes(ip_packet))

            print("New payload:", new_payload)
            print("Original length:", len(original_payload))
            print("New length:", len(new_payload))

    packet.accept()


queue = NetfilterQueue()
queue.bind(1, process_packet)

print("Testing TCP payload replacement on Device1...")

try:
    queue.run()
except KeyboardInterrupt:
    print("Stopping...")
    queue.unbind()
