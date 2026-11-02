# System Architecture

## 1. Network Overview

The project uses four Linux network namespaces to simulate two computers communicating through two intermediate security devices.

The network topology is:

```text
PC1                 Device1              Device2                 PC2
10.0.1.2            10.0.1.1             10.0.2.2                10.0.3.2
   |                    |                    |                       |
   |--------------------|                    |                       |
                    10.0.2.1 ---------------- 10.0.2.2

                                          10.0.3.1 ------------------|
```

Logical communication path:

PC1 → Device1 → Device2 → PC2

Reverse communication:

PC2 → Device2 → Device1 → PC1

## 2. Network Configuration

The environment consists of four network namespaces:

| Namespace | Interface | IP address |
|---|---|---|
| PC1 | pc1-eth0 | 10.0.1.2/24 |
| Device1 | d1-eth0 | 10.0.1.1/24 |
| Device1 | d1-eth1 | 10.0.2.1/24 |
| Device2 | d2-eth0 | 10.0.2.2/24 |
| Device2 | d2-eth1 | 10.0.3.1/24 |
| PC2 | pc2-eth0 | 10.0.3.2/24 |

Virtual Ethernet pairs connect the namespaces:

- pc1-eth0 ↔ d1-eth0
- d1-eth1 ↔ d2-eth0
- d2-eth1 ↔ pc2-eth0

IP forwarding is enabled on Device1 and Device2.

## 3. Session Establishment

Before protected TCP communication begins, Device1 and Device2 establish a shared session key.

The process uses:

1. X25519 private/public key pair generation.
2. Exchange of public keys over a TCP socket.
3. Calculation of a shared secret using X25519.
4. Derivation of a 32-byte session key using HKDF-SHA256.

Each device saves its derived key locally:

- Device1: `/tmp/device1-session.key`
- Device2: `/tmp/device2-session.key`

Both devices independently derive the same key.

## 4. TCP Connection Tracking

Both intermediate devices inspect TCP packets to identify new connections.

The connection tracker observes:

- The initial SYN packet from the client.
- The SYN-ACK packet from the server.

It uses the client and server IP addresses, port numbers, and initial sequence numbers to calculate a connection identifier using SHA-256.

This identifier is used to derive connection-specific directional encryption keys.

## 5. Directional Encryption

The system uses separate keys for each communication direction.

### PC1 to PC2

1. PC1 sends a TCP packet.
2. Device1 intercepts the packet using NFQUEUE.
3. Device1 identifies the TCP connection.
4. Device1 derives the `PC1-to-PC2` connection key.
5. The TCP payload is encrypted using AES-GCM.
6. Device1 forwards the modified packet.
7. Device2 intercepts the encrypted packet.
8. Device2 verifies its authentication tag and decrypts the payload.
9. Device2 forwards the restored packet to PC2.

### PC2 to PC1

The reverse direction follows the corresponding process:

1. PC2 sends a TCP packet.
2. Device2 intercepts the packet.
3. Device2 encrypts the TCP payload using the `PC2-to-PC1` directional key.
4. Device1 receives the encrypted packet.
5. Device1 authenticates and decrypts the payload.
6. Device1 forwards the restored packet to PC1.

## 6. Packet Processing

NFQUEUE is used to intercept forwarded TCP packets.

The packet processors:

- Inspect IPv4 and TCP headers.
- Extract the TCP payload.
- Encrypt or decrypt the payload according to the packet direction.
- Replace the original payload.
- Recalculate relevant IP and TCP lengths and checksums.
- Accept the processed packet for forwarding.

The original IP and TCP header fields are otherwise retained by the implementation.

## 7. Retransmission Handling

AES-GCM requires that a nonce must not be reused with different plaintext under the same key.

The project implements a retransmission cache.

The cache identifies a TCP segment using:

- Connection identifier
- Communication direction
- TCP sequence number
- Payload length

For an identical retransmission, the previously generated ciphertext is reused.

If different plaintext is encountered for an existing cache entry, encryption is rejected.

The cache has a maximum capacity and refuses new encryption when full.

## 8. Packet Processing Flow

```text
          Original TCP packet
                   |
                   v
             Device1
                   |
             NFQUEUE interception
                   |
             Connection tracking
                   |
             Directional key derivation
                   |
             AES-GCM encryption
                   |
                   v
             Device2
                   |
             NFQUEUE interception
                   |
             Connection tracking
                   |
             Directional key derivation
                   |
             AES-GCM authentication
                   |
             Payload decryption
                   |
                   v
                  PC2
```

The reverse direction uses the same architecture with Device2 encrypting and Device1 decrypting.

## 9. Implementation Scope

The prototype demonstrates bidirectional encryption and decryption of TCP payloads in a controlled Linux environment.

It does not implement a complete production-grade TCP security gateway. Connection lifecycle management, robust nonce management, authenticated key exchange, and MTU/fragmentation handling require further development.
