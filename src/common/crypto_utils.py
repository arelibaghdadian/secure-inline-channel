from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Generate Diffie-Hellman keys
def generate_key_pair():
    private_key = x25519.X25519PrivateKey.generate()

    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return private_key, public_bytes


# Derive the shared AES session key
def derive_session_key(private_key, peer_public_bytes):
    peer_public_key = x25519.X25519PublicKey.from_public_bytes(
        peer_public_bytes
    )

    shared_secret = private_key.exchange(peer_public_key)

    session_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-inline-channel-v1"
    ).derive(shared_secret)

    return session_key


# Encrypt a TCP payload
def encrypt_payload(session_key, nonce, plaintext):
    aes = AESGCM(session_key)

    ciphertext = aes.encrypt(nonce, plaintext, None)

    return ciphertext


# Decrypt a TCP payload
def decrypt_payload(session_key, nonce, ciphertext):
    aes = AESGCM(session_key)

    plaintext = aes.decrypt(nonce, ciphertext, None)

    return plaintext

# Derive a separate AES key for a TCP connection
def derive_connection_key(session_key, connection_id, direction):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-inline-channel-v1" + connection_id + direction
    ).derive(session_key)


# Generate a 12-byte nonce from the TCP sequence number and payload length
def generate_nonce(sequence_number, payload_length):
    if not 0 <= sequence_number <= 0xFFFFFFFF:
        raise ValueError("Invalid TCP sequence number")

    if not 0 <= payload_length <= 0xFFFF:
        raise ValueError("Invalid TCP payload length")

    nonce = (
        sequence_number.to_bytes(4, "big") +
        payload_length.to_bytes(2, "big") +
        b"\x00" * 6
    )

    return nonce
