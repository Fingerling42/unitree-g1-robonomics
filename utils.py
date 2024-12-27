def string_to_h256(input_string: str) -> str:
    """
    Function to convert regular string to H256 string for launch
    :param input_string: String to convert
    :return: 32 bytes sting
    """
    # Convert the string to bytes
    input_bytes = input_string.encode('utf-8')

    # Check if the input string is too long
    if len(input_bytes) > 32:
        raise ValueError("Input string is too long, it must be 32 bytes or less")

    # Pad the string with null bytes (b'\x00') to make it 32 bytes
    padded_bytes = input_bytes.ljust(32, b'\x00')

    return f"0x{padded_bytes.hex()}"


def h256_to_string(encoded_h256: str) -> str:

    # Check if the input starts with "0x" and remove it
    if not encoded_h256.startswith("0x"):
        raise ValueError("Input must start with '0x'")
    encoded_bytes = bytes.fromhex(encoded_h256[2:])

    # Check if the input is exactly 32 bytes
    if len(encoded_bytes) != 32:
        raise ValueError("Input must be exactly 32 bytes")

    # Decode the bytes, removing any null byte padding
    original_string = encoded_bytes.rstrip(b'\x00').decode('utf-8')

    return original_string