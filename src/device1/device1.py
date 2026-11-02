import socket
from src.common.crypto_utils import generate_key_pair, derive_session_key


HOST = "10.0.2.2"
PORT = 5000


# Generate Device1's Diffie-Hellman keys
private_key, public_key = generate_key_pair()

# Connect to Device2
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Device1 connecting to Device2...")
client.connect((HOST, PORT))

# Send Device1's public key
client.sendall(public_key)

# Receive Device2's public key
device2_public_key = client.recv(32)

# Derive the shared session key
session_key = derive_session_key(private_key, device2_public_key)

# Save the shared session key
with open("/tmp/device1-session.key", "wb") as file:
    file.write(session_key)

print("Device1 session key established successfully.")
print("Session key saved.")

client.close()
