from src.common.connection_utils import create_connection_id

# Information about the first TCP connection
connection1 = create_connection_id(
    "10.0.1.2", 50122,
    "10.0.3.2", 9000,
    1000, 2000
)

# The same connection, calculated by the other device
connection1_device2 = create_connection_id(
    "10.0.1.2", 50122,
    "10.0.3.2", 9000,
    1000, 2000
)

# A different TCP connection
connection2 = create_connection_id(
    "10.0.1.2", 50123,
    "10.0.3.2", 9000,
    3000, 4000
)

print("Same connection IDs match:", connection1 == connection1_device2)
print("Different connections have different IDs:", connection1 != connection2)
print("Connection ID length:", len(connection1))
