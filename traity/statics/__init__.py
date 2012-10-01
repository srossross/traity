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
Static properties - Validation and Defferal
=============================================

Static properties allow users to define attributes to a class ad class creation.

Unlike python's native `property` descriptor. a vproperty's getter setter and deleter are already defined.  
::

    class Foo(object):
        x = vproperty()

Normal python descriptor symantics are already defined::

    class Foo(object):
    
        @vproperty
        def x(self):
           'Getter for x'

        @x.setter
        def x(self):
           'Setter for x'


Validation
---------------------

Type and instance arguments may be given to perform arbitrary valitation before the setter is called.

::

    class Foo(object):
        x = vproperty(type=int)

    class Bar(object):
        x = vproperty(isntance=int)
        
The type argument is only required to be a function that acccepts a single input and returns a value::
    class Foo(object):
        x = vproperty(type=lambda item: item.lower())

or ::

    class Foo(object):
        x = vproperty()
        
        @x.type
        def check_x_type(self, value):
            pass 


The `instance` argument performs a strict `isinstance` check. ::

    class Foo(object):
        x = vproperty(type=int)

    class Bar(object):
        x = vproperty(isntance=int)

    foo = Foo()
    foo.x = '1' # x is set to one
    
    bar = Bar()
    bar.x = '1' # error x is not an int.
    
Delegation
---------------------

Delegation may be one of two forms, strict: and can *only* be done when the instance argument is used or loose, where no error checking is done:: 

    class Foo(object):
        x = vproperty(type=int)

    class Bar(object):
        foo = vproperty(isntance=Foo)
        
        # Strong Delegation of bar.x to bar.foo.x 
        x = foo.x
        
        # Weak delegation of bar.y to bar.foo.x
        y = delegate('foo', 'x')
        # Also can do
        y = delegate(foo, Foo.x)
'''
from traity.tools.initializable_property import persistent_property
class NoDefault: pass

class delegate(object):
    def __init__(self, outer, inner, *chain):
        if chain:
            inner = delegate(inner, *chain)
        self.outer = outer
        self.inner = inner
        
    @property
    def flat(self):
        if isinstance(self.inner, delegate):
            inners = self.inner.flat
        else:
            inners = [self.inner]
            
        return [self.outer] + inners
    
    def _get_outer(self, instance, owner=None):
        if isinstance(self.outer, str):
            obj = getattr(instance, self.outer)
        else:
            obj = self.outer.__get__(instance, owner)
        return obj
            
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        obj = self._get_outer(instance, owner)
        
        if isinstance(self.inner, str):
            return getattr(obj, self.inner)
        else:
            return self.inner.__get__(obj, owner)
    
    def __set__(self, instance, value):
        
        obj = self._get_outer(instance)
        
        if isinstance(self.inner, str):
            setattr(obj, self.inner, value)
        else:
            self.inner.__set__(obj, value)
    
    def __repr__(self):
        return "<%s '%s.%s'>" % (type(self).__name__, self.outer, self.inner)
    
    def __delete__(self, instance):
        obj = self._get_outer(instance)
        
        if isinstance(self.inner, str):
            delattr(obj, self.inner)
        else:
            self.inner.__delete__(obj)

    def __getattr__(self, attr):
        return self.delegates_to(attr)
    
    def delegates_to(self, attr):
        delegate = type(self)
        return delegate(self.outer, self.inner.delegates_to(attr))

class vproperty(persistent_property):
    '''
    Define a static attribute to a class. 
    '''
    _delegate_class_ = delegate
    def __init__(self, fget=None, fset=None, fdel=None, type=None, ftype=None, instance=None, fdefault=None):
        persistent_property.__init__(self)
        self._getter = self._default_getter if fget is None else fget
        self._setter = self._default_setter if fset is None else fset
        self._deleter = self._default_deleter if fdel is None else fdel
        if type: #Allow simple types like int, str etc
            self._type = lambda instance, value: type(value)
        else:
            self._type = ftype
            
        self._instance_of = instance
        self._default = fdefault
        
    def getter(self, value):
        self._getter = value
        return self
    
    def setter(self, value):
        self._setter = value
        return self

    def default(self, method):
        self._default = method
        return self
    
    def type(self, method):
        '''
        Set the type validation as a method of the containing class::
        
            @x.type
            def check(self, value):
               ...
    
        '''
        self._type = method
        return method
    
    def _default_getter(self, instance):
        
        has_value = hasattr(instance, self.store_key)
        if has_value or self._default is not None:
            if not has_value:
                setattr(instance, self.store_key, self._default(instance))
            return getattr(instance, self.store_key)
        else:
            raise AttributeError('Static property has not been set and has no default value')
        
    def _default_setter(self, instance, value):
        setattr(instance, self.store_key, value)
        
    def _default_deleter(self, instance):
        delattr(instance, self.store_key)
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        return self._getter(instance)
        
    def __set__(self, instance, value):
            
        if self._instance_of is not None:
            if not isinstance(value, self._instance_of):
                raise ValueError('Can not assign value of type %r (expected instance of %r)' % (type(value), self._instance_of))
        if self._type is not None:
            value = self._type(instance, value)
        
        self._setter(instance, value)
        
    def __delete__(self, instance):
        self._deleter(instance)
    
    
    def __getattr__(self, attr):
        return self.delegates_to(attr)
    
    def delegates_to(self, attr):
        '''
        Delegates to an inner attribute. instance= argument must be set in constructor.
        
        Used by __getattr__ for convinience. eg `x.delegates_to('y')` can be written as 
        `x.y`
          
        '''
        if self._instance_of is None or type(self._instance_of) is tuple:
            raise ValueError("Can not delegate to a dynamic object")
        
        delegate = type(self)._delegate_class_
        return delegate(self, getattr(self._instance_of, attr))


