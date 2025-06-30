def create_increment_callback_data(value: int) -> str:
    return f"increment:{value}"


def parse_increment_callback_data(callback_data: str) -> int:
    try:
        prefix, value_str = callback_data.split(":")
        if prefix == "increment":
            return int(value_str)
        raise ValueError("Invalid increment callback data format")
    except (ValueError, IndexError) as e:
        raise ValueError(f"Error parsing increment callback data: {e}")


def increment_value_from_callback_data(callback_data: str) -> str:
    """
    Parses the callback data, increments the value, and returns a new callback data string.
    """
    try:
        current_value = parse_increment_callback_data(callback_data)
        new_value = current_value + 1
        return create_increment_callback_data(new_value)
    except ValueError:
        # If parsing fails, return the original data to avoid breaking the flow.
        return callback_data
