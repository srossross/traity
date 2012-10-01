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
from traity.statics import vproperty
from traity.tools.initializable_property import init_properties
import pickle

@init_properties
class Picklable(object):
    p = vproperty()

class NotPicklable(object):
    p = vproperty()

class Test(unittest.TestCase):

    def test_pickle(self):
        
        should_store = Picklable()
        should_store.p = 22
        
        data = pickle.dumps(should_store)
        should_be_equal = pickle.loads(data)
        
        self.assertEqual(should_be_equal.p, should_store.p)
        
    def test_instanceof(self):
        class Obj(object):
            p = vproperty(instance=int)

        o = Obj()
        o.p = 2
        self.assertEqual(o.p, 2)
        
        with self.assertRaises(ValueError):
            o.p = '2'
        
    def test_custom_getset(self):

        class Obj(object):
            
            _q = 99
            @vproperty
            def p(self):
                return self._q + 1
            
            @p.setter
            def p(self, value):
                self._q += value
            
        o = Obj()
        self.assertEqual(o.p, 100)
        o.p = 1
        self.assertEqual(o.p, 101)
        
    def test_type(self):

        class Obj(object):
            p = vproperty(type=int)
            
        o = Obj()
        o.p = 2
        self.assertEqual(o.p, 2)
    
        o.p = '1'
        self.assertEqual(o.p, 1)
        
        with self.assertRaises(ValueError):
            o.p = 'not an int'
        
        class Obj2(object):
            p = vproperty()
            
            @p.type
            def ptype(self, value):
                return self.ty(value)
        
        o2 = Obj2()
        o2.ty = float
        
        o2.p = '1'
        
        self.assertIsInstance(o2.p, float)
        self.assertEqual(o2.p, 1.0)
        
    def test_default(self):
        
        class Obj(object):
            p = vproperty()
            
            @p.default
            def p_default(self):
                return 12
            
        o = Obj()
        
        self.assertEqual(o.p, 12)
        
        o.p = 13
        self.assertEqual(o.p, 13)
        
    def test_getter(self):
        
        class Obj(object):
            p = vproperty()
            
            @p.getter
            def p(self):
                return self.__dict__.get('_q', 1)
            
            @p.setter
            def p(self, value):
                self.__dict__['_q'] = value
                
                

        obj = Obj()
        
        self.assertEqual(obj.p, 1)
        obj.p = 2
        self.assertEqual(obj.p, 2)



    def test_getset(self):
        
        class Obj(object):
            p = vproperty()
            
        o = Obj()
        
        with self.assertRaises(AttributeError):
            o.p
            
        o.p = 1
        
        self.assertEqual(o.p, 1)
        
        del o.p
        
        with self.assertRaises(AttributeError):
            o.p
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_test_getset']
    unittest.main()
