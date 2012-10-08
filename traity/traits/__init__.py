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
from traity.tools.initializable_property import initializable
'''
Traits = Events + Statics
====================================
'''

from traity.events import events, concat_targets, Event, init_events, disconnect, \
    connect, listenable
from traity.statics import delegate , vproperty, NoDefault
import sys
import weakref

class listenable_trait(listenable):
    '''
    listenable_trait
    '''
    
    def changed(self, dispatch=None):
        def decorator(listener):
            target = concat_targets(self.target, 'changed')
            self.add_listener(target, listener)
            return listener
        return decorator

    def error(self, dispatch=None):
        def decorator(listener):
            target = concat_targets(self.target, 'error')
            self.add_listener(target, listener)
            return listener
        return decorator

class delegate_trait(delegate, listenable_trait):
    '''
    delegate_trait
    '''
    def __init__(self, outer, inner, *chain):
        delegate.__init__(self, outer, inner, *chain)
        listenable_trait.__init__(self)
    
    @property        
    def target(self):
        return tuple(self.flat)
    
    def add_listener(self, target, listener):
        '''
        Adds the listener to the outer most trait so the init_properties will pick it up. 
        '''
        self.outer.add_listener(target, listener)
        
class trait(vproperty, listenable_trait):
    '''
    
    :param fget: Is a function to be used for getting an attribute value. 
    :param fset: Is a function for setting
    :param fdel: a function for del'ing, an attribute.
    :param ftype: A type convert the argument to on `set`. `type` must be a function that 
                 accepts an argument and returns a single result. Like the builtin `int`  
    :param instance: The argument must be of this instance.
    :param fdefault: Is a function to be called when the property is not set 
    '''
    _delegate_class_ = delegate_trait
    
    def __init__(self, fget=None, fset=None, fdel=None, type=None, ftype=None, instance=None, fdefault=None):
        vproperty.__init__(self, fget=fget, fset=fset, fdel=fdel,
                           type=type, ftype=ftype, instance=instance, fdefault=fdefault)
        
        listenable_trait.__init__(self)
        
    def __init_property__(self, cls, key):
        vproperty.__init_property__(self, cls, key)
        listenable_trait.__init_property__(self, cls, key)

    #===========================================================================
    # This trait also compairs to a string! 
    #===========================================================================
    def __hash__(self):
        if self._attr is not None:
            return hash(self._attr)
        return object.__hash__(self)
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self._attr == other
        else:
            return False
     
    def __set__(self, instance, value):
        try:
            try:
                old = self._getter(instance)
            except AttributeError:
                old = NoDefault
            super(trait, self).__set__(instance, value)

        except Exception as exc:
            self.trigger(instance, 'error', exc=exc)
            raise 
        
        self.trigger(instance, 'changed', old=old, new=value)
        
        if hasattr(old, '__snitch__'):
            disconnect(instance, old, self)
            
        if hasattr(value, '__snitch__'):
            connect(instance, value, self)

class StaticListener(listenable):
    '''
    Storage container for an instance method that is being listened to statically
    '''
    def __init__(self, function):
        self.function = function
        listenable.__init__(self)
        
    def __init_property__(self, cls, key):
        
        super(StaticListener, self).__init_property__(cls, key)
        setattr(cls, key, self.function)
        return self.function

def on_trait_change(traits):
    '''
    Statically Register a listener to a class::
    
        @on_trait_change('attr')
        def attr_changed(self, event):
            print 'hello!'
    
    '''
    
    target = concat_targets(traits, 'changed')
    
    def decorator(func):
        if not isinstance(func, StaticListener):
            func = StaticListener(func)

        func.add_listener(target, func.function)
        
        return func
    
    return decorator

    
def on_change(instance, traits, function, weak=None):
    '''
    Register a listener to an object.
    
    :param traits: either a `string`, `traity.events.listenable`, or a tuple of strings and listenables.  
    :param function: function to call when event with target `target` is triggered. 
    :param instance: The object to listen to events for.
    '''
    target = concat_targets(traits, 'changed')
    events(instance).listen(target, function, weak=weak)
    
    
    
    
