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
from traity.events import concat_targets


class Test(unittest.TestCase):


    def test_concat_targets(self):
        self.assertEqual(concat_targets('a', 'b'), ('a', 'b'))
        self.assertEqual(concat_targets(('a',), 'b'), ('a', 'b'))
        self.assertEqual(concat_targets('a', ('b',)), ('a', 'b'))

        self.assertEqual(concat_targets(('a', 'b'), None), ('a', 'b'))
        self.assertEqual(concat_targets(None, ('a', 'b')), ('a', 'b'))

        self.assertEqual(concat_targets(('c'), ('a', 'b')), ('c', 'a', 'b'))
        self.assertEqual(concat_targets(('c','a'), ('b')), ('c', 'a', 'b'))

        self.assertEqual(concat_targets(None, None), None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_concat_targets']
    unittest.main()
