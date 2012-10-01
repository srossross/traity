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
from traity.events import init_events, events, queue, unique, quiet

class AnyObject(object):
    pass

class Test(unittest.TestCase):

    def test_object_context(self):
        
        obj = AnyObject()
        obj2 = AnyObject()
        init_events(obj, obj2)
        obj.id1 = 0
        obj2.id1 = 0
        
        def seen4(event):
            obj2.id1 += 1
            
        def seen3(event):
            obj.id1 += 1
            
        events(obj).on('any_target', seen3)
        events(obj).etrigger('any_target')
        self.assertEqual(obj.id1, 1)
        obj.id1 = 0
        
        events(obj2).on('any_target', seen4)
        events(obj2).etrigger('any_target')
        self.assertEqual(obj2.id1, 1)
        obj2.id1 = 0

        
        with events(obj).quiet():
            events(obj).etrigger('any_target')
            events(obj2).etrigger('any_target')
            self.assertFalse(obj.id1)
            self.assertTrue(obj2.id1)

        obj.id1 = 0
        
        with events(obj).queue() as tocall:
            events(obj).etrigger('any_target')
            events(obj).etrigger('any_target')
            self.assertFalse(obj.id1)
        
        self.assertEqual(len(tocall), 2)
        for event, listener in tocall:
            event.dispatch(listener)
        self.assertEqual(obj.id1, 2)
        
        obj.id1 = 0
        
        with events(obj).unique():
            events(obj).etrigger('any_target')
            events(obj).etrigger('any_target')
            self.assertFalse(obj.id1)

        self.assertEqual(obj.id1, 1)
    def test_global_context(self):
        
        obj = AnyObject()
        obj2 = AnyObject()
        init_events(obj, obj2)
        obj.id1 = 0
        obj2.id1 = 0
        
        def seen4(event):
            obj2.id1 += 1
            
        def seen3(event):
            obj.id1 += 1
            
        events(obj).on('any_target', seen3)
        events(obj).etrigger('any_target')
        self.assertEqual(obj.id1, 1)
        obj.id1 = 0
        
        events(obj2).on('any_target', seen4)
        events(obj2).etrigger('any_target')
        self.assertEqual(obj2.id1, 1)
        obj2.id1 = 0

        self.assertFalse(obj.id1)
        
        with quiet():
            events(obj).etrigger('any_target')
            events(obj2).etrigger('any_target')
            self.assertFalse(obj.id1)
            self.assertFalse(obj2.id1)

        obj.id1 = 0
        obj2.id1 = 0
        
        with events(obj2).quiet():
            with queue() as tocall:
                events(obj).etrigger('any_target')
                events(obj).etrigger('any_target')
                events(obj2).etrigger('any_target')
                events(obj2).etrigger('any_target')
            self.assertFalse(obj.id1)
            self.assertFalse(obj2.id1)
        
        self.assertEqual(len(tocall), 2)
        
        for event, listener in tocall:
            event.dispatch(listener)
        self.assertEqual(obj.id1, 2)
        
        obj.id1 = 0
        
        with unique():
            events(obj).etrigger('any_target')
            events(obj).etrigger('any_target')
            self.assertFalse(obj.id1)

        self.assertEqual(obj.id1, 1)
        
            
    def test_event_context(self):
        
        obj = AnyObject()
        init_events(obj)
        obj.id1 = 0
        
        def seen3(event):
            obj.id1 += 1
            
        events(obj).on('any_target', seen3)
        
        events(obj).etrigger('any_target', dispatcher=lambda event, listener:None)
        
        self.assertEqual(obj.id1, 0)

        events(obj).etrigger('any_target', dispatcher=lambda event, listener: listener(event))
        self.assertEqual(obj.id1, 1)

        with events(obj).quiet(): 
            events(obj).etrigger('any_target', dispatcher=lambda event, listener: listener(event))
            self.assertEqual(obj.id1, 2) #event dispatcher has higher priority than 'quiet'
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_simple']
    unittest.main()


