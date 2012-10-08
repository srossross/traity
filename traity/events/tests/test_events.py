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
from traity.events import init_events, events, connect, disconnect, \
    global_listener, connected, EventCycleError
import sys
import gc

class AnyObject(object):
    pass

id1, id2 = 0, 0

def seen1(event):
    global id1
    id1 += event.id1 
def seen2(event):
    global id2
    id2 += event.id2

class Test(unittest.TestCase):

    def test_shortform(self):
        global id1, id2
        id1, id2 = 0, 0
        
        obj = AnyObject()
        init_events(obj)
        
        def seen3(event):
            global id1
            id1 = True
            
        #Add a listener to target 'any_target'
        events(obj).on('any_target', seen3)
        
        #Add a trigger an 'any_target' event
        events(obj).etrigger('any_target')
        
        self.assertTrue(id1)
        
        
    def test_simple(self):
        global id1, id2
        id1, id2 = 0, 0
        
        obj = AnyObject()
        refcnt_before_init_events = sys.getrefcount(obj)
        init_events(obj)
        refcnt_after_init_events = sys.getrefcount(obj)
        self.assertEqual(refcnt_before_init_events, refcnt_after_init_events)
            
        events(obj).listen(('id1',), seen1)
        events(obj).listen(('id2',), seen2)

        events(obj).etrigger('x', id1=1, id2=2)
        self.assertEqual(id1, 0)
        self.assertEqual(id2, 0)
        
        events(obj).etrigger('id1', id1=1, id2=2)
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 0)
        
        events(obj).etrigger('id2', id1=1, id2=2)
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)
        
        events(obj).unlisten(('id1',), seen1)
        events(obj).etrigger('id1', id1=1, id2=2)
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)

        events(obj).unlisten(('id2',))
        events(obj).etrigger('id2', id1=1, id2=2)
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)
        
    def test_chain(self):
        global id1, id2
        
        id1, id2 = 0, 0
        
        obj1 = AnyObject()
        obj2 = AnyObject()
        obj3 = AnyObject()
        obj4 = AnyObject()
        
        init_events(obj1, obj2, obj3, obj4,)
        
        connect(obj1, obj2, 'c12')
        connect(obj2, obj3, 'c23')
        connect(obj2, obj4, 'c24')
        
        def seen3(event):
            global id1
            id1 = True
            self.assertEqual(event.target, ('c12', 'c23', 'x'))

        events(obj1).listen(('c12', 'c23', 'x'), seen3)
        
        events(obj3).etrigger('x')
        self.assertTrue(id1)
        
        disconnect(obj1, obj2, 'c12')
        id1 = False
        events(obj3).etrigger('x')
        self.assertFalse(id1)
        
        connect(obj1, obj2, 'c12')
        
        del obj2 #Brake Link 
        gc.collect()
        events(obj3).etrigger('x')
        self.assertFalse(id1)
        
        
    def test_add_global_litener(self):
        global id1, id2
        id1, id2 = 0, 0

        obj1 = AnyObject()
        obj2 = AnyObject()
        init_events(obj1, obj2)
        obj1.seen = 0
        obj2.seen = 0
            
        def pritn(event):
            event.obj.seen += 1
        
        with global_listener(pritn):
            events(obj1).etrigger('x')
            self.assertEqual(obj1.seen, 1)
            events(obj2).etrigger('y')
            self.assertEqual(obj2.seen, 1)
            
        events(obj1).etrigger('x')
        self.assertEqual(obj1.seen, 1)
        events(obj2).etrigger('y')
        self.assertEqual(obj2.seen, 1)
        
        with global_listener(pritn, ('x',)):
            events(obj1).etrigger('x')
            self.assertEqual(obj1.seen, 2)
            events(obj2).etrigger('y')
            self.assertEqual(obj2.seen, 1)

    def test_connected(self):
        
        obj1 = AnyObject()
        obj2 = AnyObject()
        obj3 = AnyObject()
        
        init_events(obj1, obj2, obj3)
        
        self.assertFalse(connected(obj1, obj2))
        
        connect(obj1, obj2, 'attr')
        self.assertTrue(connected(obj1, obj2))
        self.assertFalse(connected(obj2, obj1))
        
        connect(obj2, obj3, 'attr')
        self.assertTrue(connected(obj1, obj3))
        self.assertTrue(connected(obj2, obj3))
        self.assertFalse(connected(obj3,obj2))
        self.assertFalse(connected(obj3, obj1))
        
    def test_event_cycle(self):
        
        obj1 = AnyObject()
        obj2 = AnyObject()
        obj3 = AnyObject()
        
        init_events(obj1, obj2, obj3)
        
        self.assertFalse(connected(obj1, obj2))
        
        connect(obj1, obj2, 'attr')
        connect(obj2, obj3, 'attr')

        with self.assertRaises(EventCycleError):
            connect(obj3, obj1, 'attr')
        
    def test_refcount(self):
        obj = AnyObject()
        init_events(obj)
        
        class F(object):
            def m(self, event):
                return
            
        f = F()
        
        initial = sys.getrefcount(f) 
        events(obj).listen('a', f.m)
        new = sys.getrefcount(f)
        self.assertEqual(initial, new) 
        events(obj).unlisten('a', f.m)

        events(obj).listen('a', f.m, weak=False)
        new2 = sys.getrefcount(f)
        self.assertGreater(new2, initial) 
        
        events(obj).unlisten('a', f.m)
        gc.collect()
        new = sys.getrefcount(f)
        self.assertEqual(initial, new) 
        
    def test_refcount2(self):
        obj = AnyObject()
        init_events(obj)
        
        obj.x_called = 0
        def x(event):
            obj.x_called += 1
            
        self.assertEqual(obj.x_called, 0)
        events(obj).listen(('a',), x, weak=True)
        
        events(obj).etrigger('a')
        self.assertEqual(obj.x_called, 1)
        del x
        events(obj).etrigger('a')
        
        self.assertEqual(obj.x_called, 1)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_simple']
    unittest.main()
