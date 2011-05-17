import geoiq, unittest, os.path, tempfile

from geoiq.tests.functional import *

class TestUser(GeoIQFuncTest):
    def test_get_current_user(self):
        r = self.geoiq.users.current()
        self.assertTrue(r is not None)
        self.assertEquals(r.login, self.geoiq.endpoint.username)

        

if (__name__ == "__main__"):
    unittest.main()
