# Security Analysis

## 1. Introduction

This project implements a prototype of a secure inline communication channel that protects TCP payloads between two computers using two intermediate Linux devices.

The security design combines key exchange, key derivation, authenticated encryption, and connection-specific directional keys.

This document describes the cryptographic mechanisms, their security properties, and the current implementation limitations.

## 2. Key Exchange — X25519

The system uses X25519, an elliptic-curve Diffie–Hellman key exchange mechanism.

Device1 and Device2 independently generate private/public key pairs and exchange their public keys.

Each device uses its private key and the peer's public key to calculate the same shared secret.

The private keys are not exchanged.

The resulting shared secret is passed through HKDF-SHA256 to derive a 32-byte session key.

### Security property

X25519 allows two devices to establish a shared secret over a communication channel without transmitting the secret itself.

### Limitation

The current handshake does not authenticate the exchanged public keys.

Consequently, an attacker capable of intercepting and modifying the handshake could perform a man-in-the-middle attack.

An authenticated key exchange mechanism, using certificates or pre-shared authentication keys, would be required for stronger protection.

## 3. Key Derivation — HKDF-SHA256

HKDF-SHA256 is used to derive cryptographic keys from the shared secret.

The implementation derives:

- One shared session key.
- One connection-specific key for PC1-to-PC2 traffic.
- One connection-specific key for PC2-to-PC1 traffic.

The connection identifier and communication direction are included in the key derivation context.

This separates the keys used in the two communication directions.

## 4. Authenticated Encryption — AES-256-GCM

The system uses AES-256-GCM to encrypt TCP payloads.

AES-GCM provides:

- Confidentiality: the original payload is encrypted.
- Integrity: unauthorized modifications are detected.
- Authentication: the receiver verifies the authentication tag before accepting the plaintext.

The implementation uses a 32-byte AES key and a 12-byte nonce.

The authentication tag is 16 bytes long.

Therefore, the encrypted payload is 16 bytes longer than the original payload.

For example:

| Data | Size |
|---|---:|
| Original payload | 35 bytes |
| Authentication tag | 16 bytes |
| Encrypted payload | 51 bytes |

## 5. Nonce Management

AES-GCM requires that a nonce must never be reused with different plaintext under the same key.

The prototype generates a 12-byte nonce using:

- The TCP sequence number.
- The original payload length.
- A fixed six-byte padding value.

The retransmission cache stores previously encrypted segments.

If an identical segment is retransmitted, the cached ciphertext is reused instead of performing encryption again.

If different plaintext is encountered for an existing cache entry, the operation is rejected.

### Limitation

The current nonce construction is designed for the controlled prototype.

TCP sequence numbers can repeat across different connections, wrap around, or be reused in other circumstances.

The connection-specific keys reduce the scope of this risk, but the current implementation does not provide a universal guarantee of nonce uniqueness.

A production implementation should use a robust per-key nonce allocation mechanism and handle connection lifecycles and retransmissions more comprehensively.

## 6. Connection Identification

Each TCP connection is identified using:

- Client IP address and port.
- Server IP address and port.
- Client initial sequence number.
- Server initial sequence number.

The information is hashed using SHA-256 to produce a 32-byte connection identifier.

The identifier is used as part of the connection-specific key derivation process.

## 7. Retransmission Protection

The retransmission cache prevents the encryption process from generating new ciphertext with the same nonce for a different plaintext.

The cache:

- Reuses ciphertext for identical retransmissions.
- Rejects different plaintext for an existing cache entry.
- Separates entries by connection and direction.
- Has a maximum capacity.
- Refuses additional encryption when the cache is full.

The current cache does not implement a complete TCP retransmission and connection lifecycle mechanism.

## 8. Packet Integrity and Processing

Device2 verifies the AES-GCM authentication tag before decrypting PC1-to-PC2 traffic.

Device1 performs the corresponding verification for PC2-to-PC1 traffic.

If authentication fails, the ciphertext is rejected and the packet is dropped.

After successful decryption or encryption, the relevant IP and TCP lengths and checksums are recalculated.

## 9. Security Limitations

The prototype has several limitations:

1. **Unauthenticated key exchange:** X25519 public keys are not authenticated, leaving the handshake vulnerable to man-in-the-middle attacks.
2. **Nonce management:** The current sequence-number-based construction does not guarantee uniqueness in every possible TCP scenario.
3. **TCP lifecycle:** SYN retransmissions, connection termination, connection reuse, and concurrent flows are not comprehensively handled.
4. **MTU and fragmentation:** The additional 16-byte authentication tag increases packet size. MTU and fragmentation handling require further development.
5. **Limited testing environment:** The system has been tested in a controlled Linux network namespace environment and not under arbitrary production network conditions.

## 10. Conclusion

The project demonstrates how cryptographic mechanisms can be integrated into an inline packet-processing architecture.

X25519 establishes a shared secret, HKDF-SHA256 derives directional keys, and AES-256-GCM protects TCP payload confidentiality and integrity.

The successful bidirectional communication test demonstrates the basic operation of the prototype.

Further work is required before the design can be considered suitable for production deployment.
