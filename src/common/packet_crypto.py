from src.common.crypto_utils import (
    encrypt_payload,
    decrypt_payload,
    generate_nonce
)


def encrypt_tcp_payload(
    connection_key,
    cache,
    connection_id,
    direction,
    sequence_number,
    plaintext
):
    # Check whether this packet was already encrypted
    cached_payload = cache.get(
        connection_id,
        direction,
        sequence_number,
        plaintext
    )

    if cached_payload is not None:
        return cached_payload

    # Generate the nonce
    nonce = generate_nonce(
        sequence_number,
        len(plaintext)
    )

    # Encrypt the TCP payload using AES-GCM
    encrypted_payload = encrypt_payload(
        connection_key,
        nonce,
        plaintext
    )

    # Store the encrypted packet for possible retransmission
    cache.store(
        connection_id,
        direction,
        sequence_number,
        plaintext,
        encrypted_payload
    )

    return encrypted_payload


def decrypt_tcp_payload(
    connection_key,
    sequence_number,
    encrypted_payload
):
    # Remove the 16-byte AES-GCM authentication tag from the length
    plaintext_length = len(encrypted_payload) - 16

    if plaintext_length < 0:
        raise ValueError("Invalid encrypted payload")

    # Reconstruct the nonce
    nonce = generate_nonce(
        sequence_number,
        plaintext_length
    )

    # Authenticate and decrypt
    return decrypt_payload(
        connection_key,
        nonce,
        encrypted_payload
    )
