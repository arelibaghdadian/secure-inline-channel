from src.common.crypto_utils import generate_nonce

# First TCP segment
nonce1 = generate_nonce(123456, 35)

# Same segment information (for a retransmission)
nonce2 = generate_nonce(123456, 35)

# Different TCP sequence number
nonce3 = generate_nonce(123457, 35)

# Different payload length
nonce4 = generate_nonce(123456, 40)

print("Same segment produces same nonce:", nonce1 == nonce2)
print("Different sequence produces different nonce:", nonce1 != nonce3)
print("Different length produces different nonce:", nonce1 != nonce4)
