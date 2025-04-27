import hashlib
import uuid

MAX_BYTES_LENGTH = 16  # UUIDs are 128 bits (16 bytes)


def stable_id_generator(values: list[str]):
    """Generates a GUID looking string from a hash of values.
    This produces a stable ID as long as the input values are stable.
    """
    # Concatenate the values into a single string
    concatenated_values = "||".join(values).encode("utf-8")

    # Use SHA-1 hash for better distribution (160 bits)
    hashed_data = hashlib.sha1(concatenated_values).digest()

    # Truncate or pad to 16 bytes (128 bits) if needed
    if len(hashed_data) > MAX_BYTES_LENGTH:
        hashed_data = hashed_data[:MAX_BYTES_LENGTH]
    elif len(hashed_data) < MAX_BYTES_LENGTH:
        hashed_data = hashed_data.ljust(MAX_BYTES_LENGTH, b"\0")

    # Create a UUID from the hash bytes
    guid = uuid.UUID(bytes=hashed_data)
    return str(guid)
