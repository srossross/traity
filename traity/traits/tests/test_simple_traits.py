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
from traity.traits import trait, on_trait_change, on_change
from traity.events import init_events, events, global_listener
from traity.tools.initializable_property import init_properties

class Test(unittest.TestCase):


    def test_disconnect(self):
        
        @init_properties
        class B(object):
            t = trait()
            t_count = 0
            @t.changed()
            def t_changed(self, event):
                self.t_count += 1
            
        @init_properties
        class A(object):
            b = trait(instance=B)
            bt_count = 0
            
            @b.t.changed()
            def t_changed(self, event):
                self.bt_count += 1
            
        a = A()
        b1 = B()
        b2 = B()
        
        init_events(a, b1, b2)
        
        a.b = b1
        b1.t = 1
        self.assertEqual(a.bt_count, 1)
        self.assertEqual(b1.t_count, 1)
        self.assertEqual(b2.t_count, 0)
        b2.t = 1
        self.assertEqual(a.bt_count, 1)
        self.assertEqual(b1.t_count, 1)
        self.assertEqual(b2.t_count, 1)
        
        a.b = b2
        b1.t = 1
        self.assertEqual(a.bt_count, 1)
        self.assertEqual(b1.t_count, 2)
        self.assertEqual(b2.t_count, 1)
        b2.t = 1
        self.assertEqual(a.bt_count, 2)
        self.assertEqual(b1.t_count, 2)
        self.assertEqual(b2.t_count, 2)
        
        
    def test_getset_listen(self):
        
        @init_properties
        class A(object):
            t = trait()
            y = trait()
            
            @y.changed()
            def y_changed(self, event):
                self.seen_y = True
                
        a = A()
        init_events(a)
        
        a.t = 1
        
        a.seen_t = False
        a.seen_y = False
        
        def printme(event):
            a.seen_t = True
        
        on_change(a, 't', printme)
        
        a.t = 1
        self.assertTrue(a.seen_t)
        
        a.y = 1
        self.assertTrue(a.seen_y)
        
    def test_delegate_listen(self):

        @init_properties
        class C(object):
            d = trait()
        
            @d.changed()
            def d_changed(self, event):
                self.c_seen_d = True
                
        @init_properties
        class B(object):
            c = trait(instance=C)
        
            @c.changed()
            def c_changed(self, event):
                self.b_seen_c = True
                
            def __init__(self):
                self.b_seen_c = False
                self.a_seen_c = False
                init_events(self)
                
        @init_properties
        class A(object):
            b = trait(instance=B)
            c = b.c
            
            def __init__(self, b):
                self.b_seen_c = False
                self.a_seen_c = False
                init_events(self)
                self.b = b
                
            @b.c.changed()
            def c_changed(self, event):
                self.a_seen_c = True
                
        b = B()
        a = A(b)

        self.assertFalse(a.a_seen_c)
        self.assertFalse(b.b_seen_c)
        
        a.b.c = C()
        
        self.assertTrue(a.a_seen_c)
        self.assertTrue(b.b_seen_c)

        self.assertFalse(b.a_seen_c)
        self.assertFalse(a.b_seen_c)


    def test_static_listen(self):
        
        @init_properties
        class A(object):
            
            @on_trait_change('x')
            def x_changed(self, evetn):
                self.y += 1
            
        a = A()
        init_events(a)
        a.y = 0
        a.x_changed(None)
        self.assertEqual(a.y, 1)
        
        events(a).etrigger(('x', 'changed'))
        
        self.assertEqual(a.y, 2)
        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
