from netfilterqueue import NetfilterQueue


def process_packet(packet):
    print("Packet intercepted!")
    print("Packet length:", len(packet.get_payload()))

    packet.accept()


queue = NetfilterQueue()
queue.bind(1, process_packet)

print("Listening for packets in NFQUEUE 1...")

try:
    queue.run()
except KeyboardInterrupt:
    print("Stopping packet interception...")
    queue.unbind()
