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
============================
Instance properties
============================


Example ::

    class MyObj(iobject): pass
    
    def get_x(any):
        return 1
        
    obj = MyObj()
    
    set_iproperty(obj, 'x', get_x)
    
    print obj.x
    1
'''
def set_iproperty(instance, attr, prop):
    '''
    set an instance property of an object 
    '''
    instance.__instance_properties__[attr] = prop

def get_iproperty(instance, attr):
    '''
    get an instance property of an object 
    '''

    return instance.__instance_properties__[attr]

class iobject(object):
    '''
    class must be a subclass of iobject to support instance properties
    '''
    def __init__(self):
        self.__instance_properties__ = {}
        return

    def __getattribute__(self, attr):
        if attr == '__dict__':
            return object.__getattribute__(self, attr)
        
        o_dict = object.__getattribute__(self, '__dict__')
        
        instance_properties = o_dict['__instance_properties__']
        if attr in instance_properties:
            return instance_properties[attr].__get__(self, None)
        return object.__getattribute__(self, attr)
       
