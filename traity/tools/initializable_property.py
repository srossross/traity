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
'''
========================================
Initializable Properties
========================================

Properties that have knowlede of the container class.
'''

def init_properties(cls):
    '''
    Class decorator calles __init_property__ on all initializable objects defined in a class
    '''
    for key, value in list(cls.__dict__.items()):
        if isinstance(value, initializable):
            value.__init_property__(cls, key)
    return cls

class initializable(object):
    '''
    
    '''
    def __init_property__(self, cls, key):
        pass

class persistent_property(initializable):
    '''
    A persistent property. 
    '''
    def __init__(self):
        self._attr = None
        self._store_key = None

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.store_key)

    def __str__(self):
        return str(self._attr or '*')
    
    @property
    def store_key(self):
        '''
        This is set the the attribute name.
        for example:
        
        x = persistent_property()
        
        repr(x.store_key)
        '_x_'
        '''
        if self._store_key is None:
            return '_%s' %hash(self)
        return self._store_key
    
    def __init_property__(self, cls, key):
        if self._store_key is not None:
            raise ValueError("can not make persistent, this property already belongs to another class")
        self._store_key = '_%s_' % (key)
        self._attr = key
        
