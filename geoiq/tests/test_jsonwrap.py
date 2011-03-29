import geoiq.jsonwrap as jw
import unittest as ut


class TestJsonWrapProps(ut.TestCase):
    def test_simple_prop(self):
        class Foo(jw.JsonWrappedObj):
            pass

        jw.props(Foo, "hey")
        f = Foo({"hey":"you"})

        self.assertEquals(f.hey, "you")

        def failer():
            f.hey = "here"
        
        self.assertRaises(AttributeError, failer)

        class Bar(jw.JsonWrappedObj):
            writeable = True
            pass

        jw.props(Bar, "hey")

        b = Bar({"hey":"you"})
        self.assertEquals(b.hey, "you")
        b.hey = "hay!"
        self.assertEquals(b.hey, "hay!")

    def test_complex_prop(self):
        class Foo(jw.JsonWrappedObj):
            writeable = True
            pass

        def innie(x):
            return "in_" + x

        def outie(x):
            return x[len("in_"):]

        jw.props(Foo, 
                 a={
                 "ro": True
                },
                 b={
                 "map_in" : innie,
                 "map_out" : outie
                },
                 d={
                "mapto" : "c"
                })
        
        f = Foo({"a":"aaa","c":"hello"})
        def seta():
            f.a = "changed"
        self.assertRaises(AttributeError, seta)
        self.assertEquals(f.d, "hello")
        f.d = "there"
        self.assertEquals(f.d, "there")
        self.assertEquals(f.props["c"], "there")

        f = Foo.map({"b":"hello"})
        self.assertEquals(f.b, "in_hello")
        f.b="in_goodbye"
        p = f.unmap()

        self.assertEquals(p["b"], "goodbye")

        
