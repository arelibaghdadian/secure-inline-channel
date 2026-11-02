from src.common.packet_crypto import (
    encrypt_tcp_payload,
    decrypt_tcp_payload
)

from src.common.retransmission_cache import RetransmissionCache
from src.common.crypto_utils import derive_connection_key
from cryptography.exceptions import InvalidTag
from src.common.connection_utils import create_connection_id


# Load the session key established through Diffie-Hellman
with open("/tmp/device1-session.key", "rb") as file:
    session_key = file.read()


# Identify the TCP connection
connection_id = create_connection_id(
    "10.0.1.2", 50122,
    "10.0.3.2", 9000,
    1000, 2000
)

# Derive a connection-specific directional key
connection_key = derive_connection_key(
    session_key,
    connection_id,
    b"PC1-to-PC2"
)

direction = b"PC1-to-PC2"
sequence_number = 123456

# Original TCP payload
original_data = b"Hello from PC1! This is a TCP test."

# Create retransmission cache
cache = RetransmissionCache()

# First encryption
encrypted_data = encrypt_tcp_payload(
    connection_key,
    cache,
    connection_id,
    direction,
    sequence_number,
    original_data
)

print("Original length:", len(original_data))
print("Encrypted length:", len(encrypted_data))

# Simulate retransmission
retransmitted_data = encrypt_tcp_payload(
    connection_key,
    cache,
    connection_id,
    direction,
    sequence_number,
    original_data
)

print("Retransmission ciphertext matches:", encrypted_data == retransmitted_data)

# Decrypt the encrypted payload
decrypted_data = decrypt_tcp_payload(
    connection_key,
    sequence_number,
    encrypted_data
)

print("Decrypted message:", decrypted_data)
print("Original and decrypted messages match:", original_data == decrypted_data)

# Test authentication by modifying the ciphertext
modified_data = encrypted_data[:-1] + bytes([encrypted_data[-1] ^ 1])

try:
    decrypt_tcp_payload(
        connection_key,
        sequence_number,
        modified_data
    )
except InvalidTag:
    print("Tampered packet rejected: True")
