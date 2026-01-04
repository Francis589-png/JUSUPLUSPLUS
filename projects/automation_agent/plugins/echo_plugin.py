name = 'echo'

def run(context: dict) -> dict:
    """Return the received context with a message."""
    return {'message': 'echo', 'context': context}
