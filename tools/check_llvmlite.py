try:
    import llvmlite
    print('llvmlite present', getattr(llvmlite, '__version__', 'unknown'))
except Exception as e:
    print('llvmlite missing', e)
