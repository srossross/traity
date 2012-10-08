'''
Created on Oct 5, 2012

@author: sean
'''
import weakref
from types import MethodType


class method_ref(weakref.ref):

    def __new__(cls, method):

        if hasattr(method, 'im_self'):
            return weakref.ref.__new__(cls, method.im_self)
        else:
            return weakref.ref.__new__(weakref.ref, method)

    def __init__(self, method):
        super(method_ref, self).__init__(method.im_self)
        self.im_func = method.im_func
        self.im_class = method.im_class

    def __call__(self):
        im_self = super(method_ref, self).__call__()

        if im_self is None:
            return None

        return MethodType(self.im_func, im_self, self.im_class)

    def __repr__(self):
        class_name = super(method_ref, self).__call__().__class__.__name__
        return "<weakref to mthod %r on object %r" % (self.im_func.__name__, class_name)

    def __hash__(self):
        return hash(self())

    def __eq__(self, other):
        return self() == other
