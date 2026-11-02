import socket
from src.common.crypto_utils import generate_key_pair, derive_session_key


HOST = "10.0.2.2"
PORT = 5000


# Generate Device2's Diffie-Hellman keys
private_key, public_key = generate_key_pair()

# Listen for Device1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Device2 is waiting for Device1...")

connection, address = server.accept()
print("Connected to:", address)

# Receive Device1's public key
device1_public_key = connection.recv(32)

# Send Device2's public key
connection.sendall(public_key)

# Derive the shared session key
session_key = derive_session_key(private_key, device1_public_key)

# Save the shared session key
with open("/tmp/device2-session.key", "wb") as file:
    file.write(session_key)

print("Device2 session key established successfully.")
print("Session key saved.")

connection.close()
server.close()
