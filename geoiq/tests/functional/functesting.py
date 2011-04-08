import geoiq, unittest

try:
    import simplejson as json
except ImportError:
    import json


class FuncTest(unittest.TestCase):
    # TODO: explicit tagging of errors to steps?
    pass

# Testing steps --- basically functions wrapped with a little bit o' goop
#  to make tagging errors (TODO) in them easier.
# Placeholder decorator:
def step():
    def r(inner):
        def res(*args,**kwargs):
            return inner(*args,**kwargs)
        res.__name__ = inner.__name__
        return res
    return r

