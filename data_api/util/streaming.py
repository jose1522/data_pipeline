import io


def buffer_to_generator(buffer: io.StringIO):
    """Convert a buffer to a generator.
    This is useful for creating streaming responses
    Args:
        buffer (io.StringIO): A buffer containing the data to be streamed
    """
    buffer.seek(0)
    yield buffer.getvalue()
