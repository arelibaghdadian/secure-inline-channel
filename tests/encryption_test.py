from src.common.crypto_utils import encrypt_payload, decrypt_payload

# Load the session key established through Diffie-Hellman
with open("/tmp/device1-session.key", "rb") as file:
    session_key = file.read()

# Original message
message = b"Hello from PC1! This is a TCP test."

# Test nonce (12 bytes)
nonce = b"D1toD2!!" + (123456).to_bytes(4, "big")

# Encrypt
encrypted = encrypt_payload(session_key, nonce, message)

# Decrypt
decrypted = decrypt_payload(session_key, nonce, encrypted)

print("Original message:", message)
print("Encrypted message:", encrypted.hex())
print("Encrypted length:", len(encrypted))
print("Decrypted message:", decrypted)
print("Messages match:", message == decrypted)
