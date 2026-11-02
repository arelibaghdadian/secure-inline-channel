class RetransmissionCache:

    def __init__(self, max_entries=10000):
        self.cache = {}
        self.max_entries = max_entries

    def get(self, connection_id, direction, sequence_number, plaintext):
        key = (
            connection_id,
            direction,
            sequence_number,
            len(plaintext)
        )

        if key in self.cache:
            original_plaintext, encrypted_payload = self.cache[key]

            if original_plaintext != plaintext:
                raise ValueError(
                    "Different data found for an existing TCP segment"
                )

            print("Retransmission detected. Reusing cached ciphertext.")
            return encrypted_payload

        return None

    def store(
        self,
        connection_id,
        direction,
        sequence_number,
        plaintext,
        encrypted_payload
    ):
        key = (
            connection_id,
            direction,
            sequence_number,
            len(plaintext)
        )

        if key in self.cache:
            original_plaintext, _ = self.cache[key]

            if original_plaintext != plaintext:
                raise ValueError(
                    "Cannot reuse nonce for different plaintext"
                )

            return

        if len(self.cache) >= self.max_entries:
            raise RuntimeError(
                "Retransmission cache is full. Stop encryption and rekey."
            )

        self.cache[key] = (plaintext, encrypted_payload)
