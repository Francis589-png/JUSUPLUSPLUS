name = 'time'

def run(context: dict) -> dict:
    import time
    return {'time': time.time()}
