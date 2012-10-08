'''
Created on Oct 8, 2012

@author: sean
'''
from traity.traits import trait

class Int(trait):
    def __init__(self, default=0):
        trait.__init__(self, type=int, fdefault=lambda self:default)
    
    # Special method to allow trait to be called with or without parens '()'
    # Method __init_property__ is invoked when init_properties is called
    
    @classmethod
    def __init_property__(cls, owner, key):
        int_trait = cls()
        setattr(owner, key, int_trait)
        trait.__init_property__(int_trait, owner, key)
