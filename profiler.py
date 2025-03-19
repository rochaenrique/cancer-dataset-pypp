import time

class Profile:
    _header = '--------------------------------------------------'
    def __init__(self, label):
        self._label = label
        
    def __enter__(self):
        print(self._header)
        self._time = time.time()
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            print(f'{repr(self._label):20}: {time.time() - self._time:.5f}s')
        else:
            print(f'Failed due to: {exc_type.__name__}')
        print(self._header)
