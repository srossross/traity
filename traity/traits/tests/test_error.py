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
from traity.tools.initializable_property import init_properties
from traity.traits import trait
from traity.events import init_events


class Test(unittest.TestCase):


    def test_error_notifyer(self):
        
        class MyExc(Exception): pass
        @init_properties
        class A(object):
            y = trait()
            seen_y_error = False
            
            @y.setter
            def y(self, value):
                self._y = value
                raise MyExc()
             
            @y.changed()
            def y_changed(self, event):
                self.seen_y = True
                
            @y.error()
            def y_error(self, event):
                self.seen_y_error = True
                
        
        a = A() 
        init_events(a)
        
        with self.assertRaises(MyExc):
            a.y = 1
        
        self.assertTrue(a.seen_y_error)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_error_notifyer']
    unittest.main()
