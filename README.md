# Secure Inline Communication Channel

## Overview

This project implements a prototype of a secure inline communication channel between two computers using two intermediate Linux devices.

The system intercepts TCP packets, encrypts their payloads using AES-GCM, and decrypts them at the receiving intermediate device before forwarding them to the destination.

The communication is protected in both directions:

- PC1 → Device1 → Device2 → PC2
- PC2 → Device2 → Device1 → PC1

The project was developed and tested in Kali Linux using Linux network namespaces and VirtualBox.

## Architecture

The network consists of four isolated network namespaces:

| Node | Interface | IP address |
|---|---|---|
| PC1 | pc1-eth0 | 10.0.1.2 |
| Device1 | d1-eth0 | 10.0.1.1 |
| Device1 | d1-eth1 | 10.0.2.1 |
| Device2 | d2-eth0 | 10.0.2.2 |
| Device2 | d2-eth1 | 10.0.3.1 |
| PC2 | pc2-eth0 | 10.0.3.2 |

Device1 and Device2 act as intermediate packet-processing devices.

## Technologies

- **Python** – implementation language
- **Scapy** – packet inspection and modification
- **NetfilterQueue** – interception of forwarded packets
- **X25519** – Diffie–Hellman key exchange
- **HKDF-SHA256** – session and directional key derivation
- **AES-256-GCM** – payload encryption and authentication
- **Linux network namespaces** – isolated network topology
- **iptables** – packet filtering and NFQUEUE redirection

## How It Works

### 1. Session Establishment

Device1 and Device2 establish a shared session key using X25519 key exchange.

Both devices independently derive the same 32-byte session key.

### 2. Connection Tracking

The intermediate devices inspect TCP connection establishment packets.

They use the client and server IP addresses, ports, and initial sequence numbers to calculate a connection identifier.

### 3. Directional Key Derivation

Separate connection-specific encryption keys are derived for:

- PC1-to-PC2 traffic
- PC2-to-PC1 traffic

HKDF-SHA256 is used to derive these keys from the shared session key.

### 4. Encryption

Device1 encrypts the TCP payload of PC1-to-PC2 packets using AES-GCM.

The encrypted payload includes the authentication tag.

### 5. Decryption

Device2 verifies the authentication tag and decrypts the payload before forwarding the packet to PC2.

### 6. Reverse Communication

The same process is performed in reverse:

Device2 encrypts PC2-to-PC1 traffic, and Device1 decrypts it.

### 7. Packet Forwarding

The intermediate devices replace the TCP payload and recalculate the relevant IP and TCP lengths and checksums before accepting the packet.

## Project Structure

```text
secure-inline-channel/
├── src/
│   ├── common/
│   │   ├── connection_utils.py
│   │   ├── crypto_utils.py
│   │   ├── packet_crypto.py
│   │   ├── retransmission_cache.py
│   │   └── tcp_connection_tracker.py
│   ├── device1/
│   │   ├── device1.py
│   │   └── encryptor.py
│   └── device2/
│       ├── device2.py
│       └── decryptor.py
├── tests/
├── docs/
│   └── screenshots/
├── README.md
└── .gitignore
```

## Requirements

The project requires Python 3 and the following packages:

- Scapy
- cryptography
- NetfilterQueue

The Linux environment also requires iptables, Linux network namespace support, and the necessary NFQUEUE libraries.

## Testing

The project includes tests for:

- AES-GCM encryption and decryption
- Packet payload encryption and decryption
- Authentication and tampering detection
- Nonce generation
- TCP connection identification
- TCP connection tracking
- Retransmission caching
- NFQUEUE binding

Tests can be executed from the project root using:

```bash
PYTHONPATH=. python3 tests/encryption_test.py
PYTHONPATH=. python3 tests/packet_crypto_test.py
PYTHONPATH=. python3 tests/nonce_test.py
PYTHONPATH=. python3 tests/connection_test.py
PYTHONPATH=. python3 tests/connection_tracker_test.py
PYTHONPATH=. python3 tests/cache_test.py
```

The NFQUEUE binding test requires root privileges:

```bash
sudo env PYTHONPATH=. python3 tests/queue_test.py
```

A successful end-to-end test demonstrated bidirectional TCP communication through Device1 and Device2, with payload encryption and decryption in both directions.

## Screenshots

The `docs/screenshots/` directory contains screenshots documenting the network configuration, key exchange, packet interception, encryption tests, and bidirectional communication.

## Security Considerations and Limitations

This implementation is an educational prototype and is not intended for production deployment.

Important limitations include:

- The X25519 key exchange is not authenticated and is therefore vulnerable to man-in-the-middle attacks.
- Nonce generation is based on TCP sequence numbers and payload lengths. The current approach is intended for the bounded prototype and does not guarantee uniqueness in every possible TCP scenario.
- TCP retransmission handling uses a bounded cache and does not implement a complete TCP connection lifecycle.
- MTU, fragmentation, and large-packet handling require further development.
- Connection tracking does not yet handle every possible TCP lifecycle event or concurrency scenario.
- The implementation has been tested in a controlled Linux network environment.

## Future Improvements

- Authenticate the key exchange.
- Improve nonce management and TCP retransmission handling.
- Implement complete connection lifecycle management.
- Improve MTU and fragmentation handling.
- Add more extensive automated integration tests.
- Improve error handling and logging.

## Project Status

The prototype successfully demonstrates bidirectional TCP payload encryption and decryption between two computers through two intermediate Linux devices.
