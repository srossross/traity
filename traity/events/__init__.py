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
Event system
=============

This is a **pure** event handling and propegation framework. 

'''

import weakref
import re
from contextlib import contextmanager
from types import MethodType
from traity.tools.initializable_property import initializable

def concat_targets(left, right):
    '''
    concatinate targets with target into a tuple.
    '''
    if left is None:
        left = ()
    elif not isinstance(left, tuple):
        left = (left,)
    if right is None:
        right = ()
    elif not isinstance(right, tuple):
        right = (right,)
    target = left + right
    if not target:
        return None
    return target
            
class Event(object):
    '''
    An event should never need to be created directly.  Use `events(obj).etrigger` to start a chain of events.
    
    :param event_type: type of event
    :param target: 
    
    
    '''
    _GLOBAL_DISPATCH_ = []
    def __init__(self, snitch, target, dispatcher=None, **kwargs):
        self.snitch = snitch
        self._target = target
        self.__dict__.update(kwargs)
        self._kwargs = kwargs
        self.stop = False
        self.dispatcher = dispatcher
        
    
    @property
    def obj(self):
        return self.snitch._instance()
    @property
    def target(self):
        '''
        The target this event will trigger action for.
        '''
        return self._target
    
    
    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        if self.target != other.target:
            return False
        if self.snitch is not other.snitch:
            return False
        
        return True
    
    def __hash__(self):
        return hash(self.target) + 1
        
    def __repr__(self):
        return "Event(%(_target)r)" % self.__dict__
        
    def bubble_target(self, snitch, target):
        '''
        returns a new event with target prepended to the list of targets.
        '''
        target = concat_targets(target, self.target)
        dispatcher = self.dispatcher
        return Event(snitch, target, dispatcher, **self._kwargs)
    
    def dispatch(self, listener):
        if self.dispatcher:
            self.dispatcher(self, listener)
        elif self.snitch._dispatch_stack_:
            self.snitch._dispatch_stack_[-1](self, listener)
        elif type(self)._GLOBAL_DISPATCH_:
            type(self)._GLOBAL_DISPATCH_[-1](self, listener)
            
        else:
            listener(self)
        
def add_global_listener(listener, target=None):
    glbl = Snitch.global_listeners.setdefault(target, [])
    glbl.append(listener)
    
def remove_global_listener(listener, target=None):
    glbl = Snitch.global_listeners.setdefault(target, [])
    if listener in glbl: 
        glbl.remove(listener)
    
@contextmanager
def global_listener(listener, target=None):
    add_global_listener(listener, target)
    yield
    remove_global_listener(listener, target)
    
@contextmanager
def quiet():
    Event._GLOBAL_DISPATCH_.append(lambda event, listener: setattr(event, 'stop', True))
    yield
    Event._GLOBAL_DISPATCH_.pop()

@contextmanager
def queue():
    todo = []
    Event._GLOBAL_DISPATCH_.append(lambda event, listener: todo.append((event, listener)))
    yield todo
    Event._GLOBAL_DISPATCH_.pop()

@contextmanager
def unique():
    todo = set()
    Event._GLOBAL_DISPATCH_.append(lambda event, listener: todo.add((event, listener)))
    yield
    
    Event._GLOBAL_DISPATCH_.pop()
    
    for event, listener in todo:
        event.dispatch(listener)
    



class Snitch(object):
    '''
    Snitch object handles events. and propegates them to the object's parents 
    '''
    _GLOBAL_DISPATCH_ = []
    global_listeners = {}
    def __init__(self, instance):
        self._instance = weakref.ref(instance)

        self._parents = weakref.WeakKeyDictionary()
        
        self._listeners = {}
        cls = type(instance)
        
        if hasattr(cls, '__listeners__'):
            for key, listeners in instance.__listeners__.items():
                ilisteners = self._listeners.setdefault(key, [])
                for listener in listeners: 
                    ilisteners.append(MethodType(listener, instance))
                
        self._dispatch_stack_ = []
        
    @contextmanager
    def quiet(self, stop=True):
        '''
        Context manager to stop events being propegated.
        '''
        self._dispatch_stack_.append(lambda event, listener: setattr(event, 'stop', stop))
        yield
        self._dispatch_stack_.pop()
        
    @contextmanager
    def queue(self):
        todo = []
        self._dispatch_stack_.append(lambda event, listener: todo.append((event, listener)))
        yield todo
        self._dispatch_stack_.pop()
    
    @contextmanager
    def unique(self):
        todo = set()
        self._dispatch_stack_.append(lambda event, listener: todo.add((event, listener)))
        yield todo
        self._dispatch_stack_.pop()
        for event, listener in todo:
            event.dispatch(listener)
    
    def etrigger(self, target, **metadata):
        event = Event(self, (target,), **metadata)
        self.trigger(event)
        
    def group_dispatch(self, listeners, event):
        if listeners:
            for listener in listeners.get(event.target, []):
                event.dispatch(listener)
                if event.stop: return 
                
            for listener in listeners.get(None, []):
                event.dispatch(listener)
                if event.stop: return
                
    def trigger(self, event):
        self.group_dispatch(self._listeners, event)
        self.group_dispatch(type(self).global_listeners, event)
        self.bubble(event)
        
    def __repr__(self):
        return '<%s for %r>' % (type(self).__name__, self._instance())
    

    def add_parent(self, parent_snitch, target):
        '''
        Add a parent
        '''
        self._parents.setdefault(parent_snitch, set()).add(target)
            
    def remove_parent(self, parent_snitch, target):
        '''
        Remove a parent
        '''
        targets = self._parents.get(parent_snitch, set())
        targets.discard(target)
    
    def bubble(self, event):
        '''
        Propagate this event up to parents connected with 'connect'.
        '''
        for parent, targets in self._parents.items():
            for target in targets: 
                event_new = event.bubble_target(parent, target)
                parent.trigger(event_new)
                if event_new.stop:
                    event.stop = True
                    return

    def listen(self, target, listener):
        '''
        Add a listener to listen to events with target 'target'.
        '''
        listeners = self._listeners.setdefault(target , [])
        listeners.append(listener)
            
    def unlisten(self, target, listener=None):
        '''
        Remove a listener. 
        '''
        if target in self._listeners:
            if listener is None:
                del self._listeners[target]
            elif listener in self._listeners[target]:
                self._listeners[target].remove(listener)
    
    def on(self, target, listener):
        self.listen((target,), listener)
        
    
def connect(parent, child, target, init=True):
    '''
    Connect two objects together so that events will bubble upward from child to parent.
    '''
    child_snitch = events(child)
    parent_snitch = events(parent)
    child_snitch.add_parent(parent_snitch, target)

def disconnect(parent, child, target, init=True):
    '''
    Discnnect two objects.
    '''
    child_snitch = events(child, init)
    parent_snitch = events(parent, init)
    child_snitch.remove_parent(parent_snitch, target)
    
def events(instance, init=False):
    '''
    Get the events class associated with this object. 
    If init is true. call init_events if events are uninitialized, otherwize, raise an 
    exception.
    '''
    if init and not hasattr(instance, '__snitch__'):
        init_events(instance)
     
    return instance.__snitch__

def init_events(*instances):
    '''
    Initialize the events for an object
    '''
    for instance in instances:
        instance.__snitch__ = Snitch(instance)
    

class listenable(initializable):
    
    def __init__(self):
        self._listeners = {}
        
    def add_listener(self, target, listener):
        self._listeners.setdefault(target, []).append(listener)
    
    def listen_to(self, target=None):
        def decorator(listener):
            self.add_listener(target, listener)
        return decorator

    @property
    def target(self):
        return self
    
    def trigger(self, obj, target=None, **metadata):
        target = concat_targets(self.target, target)
        snch = events(obj)
        event = Event(snch, target, **metadata)
        snch.trigger(event)
        
    def __init_property__(self, cls, key):
        if '__listeners__' not in cls.__dict__:
            listeners = {}
            base_listeners = getattr(cls, '__listeners__', {})
            setattr(cls, '__listeners__', listeners)
            
            for key, functions in base_listeners.items():
                base_listeners.setdefault(key, []).extend(functions)
        else:    
            listeners = cls.__dict__['__listeners__']
            
        for key, functions in self._listeners.items():
            listeners.setdefault(key, []).extend(functions)
                
        
            
