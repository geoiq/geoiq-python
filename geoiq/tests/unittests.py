import unittest as ut

from test_jsonwrap import *
from test_dataset import *

try: from test_features import *
except ImportError:   
    print("WARNING: shapely not installed; missing some tests.")

if __name__ == "__main__":
    ut.main()
