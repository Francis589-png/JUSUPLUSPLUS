import importlib, sys, os
print('cwd:', os.getcwd())
print('sys.path[0]:', sys.path[0])
print('exists projects:', os.path.exists('projects'))
try:
    m = importlib.import_module('projects')
    print('projects imported from', getattr(m, '__file__', getattr(m, '__path__', None)))
except Exception as e:
    print('import failed', e)
    sys.exit(1)
