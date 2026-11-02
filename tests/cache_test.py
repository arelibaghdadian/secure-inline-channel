from src.common.retransmission_cache import RetransmissionCache

cache = RetransmissionCache()

connection_id = b"connection_1"
direction = b"PC1-to-PC2"

sequence_number = 123456
original_data = b"Hello from PC1!"
encrypted_data = b"encrypted_data_example"

cache.store(
    connection_id,
    direction,
    sequence_number,
    original_data,
    encrypted_data
)

print("First transmission stored.")

cached_data = cache.get(
    connection_id,
    direction,
    sequence_number,
    original_data
)

print("Cached ciphertext matches:", cached_data == encrypted_data)

try:
    cache.get(
        connection_id,
        direction,
        sequence_number,
        b"Wrong message!!"
    )
except ValueError as error:
    print("Different data rejected:", error)

# Test connection isolation
connection2 = b"connection_2"

result1 = cache.get(
    connection2,
    direction,
    sequence_number,
    original_data
)

print("Different connection has independent cache:", result1 is None)


# Test direction isolation
reverse_direction = b"PC2-to-PC1"

result2 = cache.get(
    connection_id,
    reverse_direction,
    sequence_number,
    original_data
)

print("Different direction has independent cache:", result2 is None)
