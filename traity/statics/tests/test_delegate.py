#-------------------------------------------------------------------------------
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Sean Ross-Ross
#
#-------------------------------------------------------------------------------

import unittest
from traity.statics import vproperty, delegate
from traity.tools.initializable_property import init_properties

class InnerObject(object):
    
    x = vproperty(fdefault=lambda self: 99)
    y = vproperty()
    nx = vproperty(type=int, fdefault=lambda self: 0)

class TestObject(object):
    
    inner = vproperty(instance=InnerObject)
    x = inner.x
    y = inner.y

    nix = vproperty(type=int, fdefault=lambda self: 0)
    niy = vproperty(type=int, fdefault=lambda self: 0)

class Test(unittest.TestCase):

    def test_cant_delegate(self):
        class Obj(object):
            p = vproperty(type=int)
            
            with self.assertRaises(ValueError):
                p.delegates_to('x')
        
    def test_getset_weak(self):
        class Del(object):
            d = delegate('a', 'b', 'c', 'd')
            
        class Obj(object): pass
        
        
        o = Del()
        
        with self.assertRaises(AttributeError):
            o.d
            
        o.a = Obj()
        o.a.b = Obj()
        o.a.b.c = c = Obj()
        o.a.b.c.d = d = Obj()
    
        self.assertIs(o.d, d)
        o.d = 1
        self.assertEqual(o.d, 1)
        
        del o.d
        
        with self.assertRaises(AttributeError):
            o.d
        with self.assertRaises(AttributeError):
            c.d
    
    def test_getset_strict(self):

        self.assertTrue(isinstance(TestObject.inner, vproperty))
        self.assertTrue(isinstance(TestObject.x, delegate))

        subject = TestObject()
        inner1 = InnerObject()

        with self.assertRaises(AttributeError):
            subject.inner
        with self.assertRaises(AttributeError):
            subject.y
#            subject.inne
            
        subject.inner = inner1

        self.assertEqual(subject.inner, inner1)
        self.assertEqual(subject.x, 99)

        subject.inner.x = 1

        self.assertEqual(subject.x, 1)

        self.assertEqual(subject.inner.x, 1)
        self.assertEqual(subject.inner.x, subject.x)

        del subject.inner.x 
        self.assertEqual(subject.inner.x, 99)
        
        subject.y = 122
        self.assertEqual(subject.inner.y, 122)
        del subject.inner.y
        with self.assertRaises(AttributeError):
            subject.y
            
        subject.x = 0
        subject.y = 122
    
        inner2 = InnerObject()
        subject.inner = inner2
        
        self.assertEqual(subject.inner, inner2)
        self.assertEqual(subject.x, 99)
        
    def test_nested_strict(self):
        @init_properties
        class InnerInner(object):
            def __init__(self, x): self.x = x
            x = vproperty()
            nx = vproperty(fdefault=lambda self:0, type=int)

        @init_properties
        class Inner(object):
            def __init__(self, ii): self.ii = ii
            ii = vproperty(instance=InnerInner)
            nx = ii.nx
            x = ii.x

        @init_properties
        class Outer(object):
            def __init__(self, i): self.i = i
            i = vproperty(instance=Inner)
            y = i.ii
            nx = y.nx
            x = i.ii.x
            
        self.assertEqual(Outer.x.flat, [Outer.i, Inner.ii, InnerInner.x])
        
        ii = InnerInner(x=1)
        i = Inner(ii=ii)
        outer = Outer(i=i)

        self.assertEqual(outer.i.ii.nx, 0)
        self.assertEqual(ii.nx, 0)
        self.assertEqual(outer.i.nx, 0)
        self.assertEqual(outer.nx, 0)
        
        self.assertIs(outer.i.ii, outer.y)
        
        outer.x = 'non'

        self.assertEqual(outer.x, 'non')

        ii2 = InnerInner(x=1)
        outer.i.ii = ii2

        self.assertEqual(outer.i.ii.nx, 0)

        self.assertEqual(outer.x, 1)

        outer.x = 'now'
        self.assertEqual(outer.x, 'now')
        self.assertEqual(outer.i.x, 'now')
        self.assertEqual(outer.i.ii.x, 'now')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_test_getset']
    unittest.main()
