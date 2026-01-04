def load():
    """Return a module-like object for the plugin."""
    class Mod:
        def hello(self):
            return 'hello from example plugin'

        def add(self, a, b):
            return a + b

    return Mod()
