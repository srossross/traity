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
=============
Event system
=============

This is a **pure** event handling and propegation framework. 

'''

import weakref
import re
from contextlib import contextmanager
from types import MethodType
from traity.tools.initializable_property import initializable

class EventError(Exception):
    pass

class EventCycleError(EventError):
    pass

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
        '''
        call a listener object
        '''
        if self.dispatcher:
            self.dispatcher(self, listener)
        elif self.snitch._dispatch_stack_:
            self.snitch._dispatch_stack_[-1](self, listener)
        else:
            listener(self)
        
def add_global_listener(listener, target=None):
    '''
    Add a listener to events on all objects.
    '''
    glbl = Snitch.global_listeners.setdefault(target, [])
    glbl.append(listener)
    
def remove_global_listener(listener, target=None):
    '''
    remove a add_global_listener
    '''

    glbl = Snitch.global_listeners.setdefault(target, [])
    if listener in glbl: 
        glbl.remove(listener)
    
@contextmanager
def global_listener(listener, target=None):
    '''
    Context manager for global listeners::
    
        def print_event(event):
            print event
            
        with global_listener(print_event):
            ...
        
    '''
    add_global_listener(listener, target)
    yield
    remove_global_listener(listener, target)
    
def add_global_dispatcher(dispatcher):
    Snitch._GLOBAL_DISPATCHERS_.append(dispatcher)
    for snitch in Snitch.__instances__:
        snitch._dispatch_stack_.append(dispatcher)

def pop_global_dispatcher():
    Snitch._GLOBAL_DISPATCHERS_.pop()
    for snitch in Snitch.__instances__:
        snitch._dispatch_stack_.pop()

def remove_global_dispatcher(dispatcher):
    for snitch in Snitch.__instances__:
        dstack = snitch._dispatch_stack_
        if dispatcher in dstack:
            idx = dstack[::-1].index(dispatcher)
            del dstack[len(dstack) - idx - 1]
            
    dstack = Snitch._GLOBAL_DISPATCHERS_
    if dispatcher in dstack:
        idx = dstack[::-1].index(dispatcher)
        del dstack[len(dstack) - idx - 1]
            

@contextmanager
def global_dispatcher(dispatcher):
    add_global_dispatcher(dispatcher)
    yield
    pop_global_dispatcher()
    
@contextmanager
def quiet():
    '''
    Do not dispatch any events
    '''
    dispatcher = lambda event, listener: setattr(event, 'stop', True)
    add_global_dispatcher(dispatcher)
    yield
    pop_global_dispatcher()

@contextmanager
def queue():
    '''
    Put all events into a queue.
    
    eg::
    
        with queue() as todo:
            ...
        
        print "I have cought %i events" % len(todo)
    '''

    todo = []
    dispatcher = lambda event, listener: todo.append((event, listener))
    add_global_dispatcher(dispatcher)
    yield todo
    pop_global_dispatcher()

@contextmanager
def unique():
    '''
    Only process unique events eg::
    
        num_calls = 0
        with global_listener(inc_num_calls):
            with unique():
                triggers_event()
                triggers_event()
        
        assert num_calls == 1 
    
    '''
    todo = set()
    dispatcher = lambda event, listener: todo.add((event, listener))
    add_global_dispatcher(dispatcher)
    yield
    pop_global_dispatcher()
    
    for event, listener in todo:
        event.dispatch(listener)



class Snitch(object):
    '''
    Snitch object handles events. and propegates them to the object's upstream nodes 
    '''
    __instances__ = weakref.WeakSet()
    _GLOBAL_DISPATCHERS_ = []
    global_listeners = {}
    def __init__(self, instance):
        self._instance = weakref.ref(instance)

        self._upstream = weakref.WeakKeyDictionary()
        
        self._listeners = {}
        cls = type(instance)
        
        if hasattr(cls, '__listeners__'):
            for key, listeners in instance.__listeners__.items():
                ilisteners = self._listeners.setdefault(key, [])
                for listener in listeners: 
                    ilisteners.append(MethodType(listener, instance))
                
        self._dispatch_stack_ = list(self._GLOBAL_DISPATCHERS_)
        self.__instances__.add(self)
        
        
    def add_dispatcher(self, dispatcher):
        self._dispatch_stack_.append(dispatcher)

    def pop_dispatcher(self):
        self._dispatch_stack_.pop()
        
    @contextmanager
    def quiet(self, stop=True):
        '''
        Context manager to stop events being propegated.
        '''
        dispatcher = lambda event, listener: setattr(event, 'stop', stop)
        self.add_dispatcher(dispatcher)
        yield
        self.pop_dispatcher()
        
    @contextmanager
    def queue(self):
        todo = []
        dispatcher = lambda event, listener: todo.append((event, listener))
        self.add_dispatcher(dispatcher)
        yield todo
        self.pop_dispatcher()
    
    @contextmanager
    def unique(self):
        todo = set()
        dispatcher = lambda event, listener: todo.add((event, listener))
        
        self.add_dispatcher(dispatcher)
        yield
        self.pop_dispatcher()
        
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
    

    def add_upstream(self, node, target):
        '''
        Add a upstream connection
        '''
        self._upstream.setdefault(node, set()).add(target)
            
    def remove_upstream(self, node, target):
        '''
        Remove a node from upstream connections
        '''
        targets = self._upstream.get(node, set())
        targets.discard(target)
    
    def bubble(self, event):
        '''
        Propagate this event up to upstream nodes connected with 'connect'.
        '''
        for node, targets in self._upstream.items():
            for target in targets: 
                event_new = event.bubble_target(node, target)
                node.trigger(event_new)
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
        
    
def _sn_connected(us_snitch, ds_snitch):
    '''
    Test if to snitch objects are connected.
    '''

    if us_snitch is ds_snitch:
        return True
    
    for node in ds_snitch._upstream.keys():
        if _sn_connected(us_snitch, node):
            return True

    return False
    
def connected(upstream, downstream):
    '''
    Test if to objects are connected.
    '''
    ds_snitch = events(downstream)
    us_snitch = events(upstream)
    
    return _sn_connected(us_snitch, ds_snitch)

def connect(upstream, downstream, target, init=True):
    '''
    Connect two objects together so that events will bubble upstream.
    '''
    if connected(downstream, upstream):
        raise EventCycleError('Can not connect %r to %r' % (upstream, downstream))
    
    ds_snitch = events(downstream)
    us_snitch = events(upstream)
    ds_snitch.add_upstream(us_snitch, target)

def disconnect(upstream, downstream, target, init=True):
    '''
    Discnnect two objects.
    '''
    ds_snitch = events(downstream, init)
    us_snitch = events(upstream, init)
    ds_snitch.remove_upstream(us_snitch, target)
    
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
                
        
            
