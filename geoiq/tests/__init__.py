#


# Helper decorator for repeating a test (or other stuff?):
class repeated(object):
    def __init__(self, count):
        self.count = count

    def __call__(self, f):
        def r(*args,**kwargs):
            return [ f(*args,**kwargs) for x in range(self.count) ]
        r.__name__ = f.__name__
        return r


