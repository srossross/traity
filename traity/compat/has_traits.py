'''
Created on Oct 8, 2012

@author: sean
'''
from traity.tools.initializable_property import init_properties
from traity.events import init_events

    
class HasTraitsMeta(type):
    def __new__(cls, name, bases, dct):
        Klass = type.__new__(cls, name, bases, dct)
        init_properties(Klass)
        return Klass
     
class HasTraits(object):
    __metaclass__ = HasTraitsMeta
   
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        init_events(self)
