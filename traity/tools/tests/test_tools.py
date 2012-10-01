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
from traity.tools.initializable_property import persistent_property, \
    init_properties


class Test(unittest.TestCase):


    def test_iproperty(self):
        
        class A(object):
            p = persistent_property()
        
        
        self.assertEqual(A.p._attr, None) 
        self.assertEqual(A.p._store_key, None)
         
        init_properties(A)
        
        self.assertEqual(A.p._attr, 'p') 
        self.assertEqual(A.p._store_key, '_p_')
        
        with self.assertRaises(ValueError):
            init_properties(A)
            
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_iproperty']
    unittest.main()
