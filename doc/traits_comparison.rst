============================
Comparison with traits
============================

My ideal traits's like library.

traity.events + traity.statics == traity.traits.  

### Objectives

#### Uphold the main principles and philosophy of traits 

Initialization: 
    A may optionally have a default value.
    
Validation:
    A trait attribute is explicitly typed. 
    The type of a trait-based attribute is evident in the code, and only values that meet a programmer-specified set of criteria (i.e., the trait definition) can be assigned to that attribute. 
    
Deferral: 
    The value of a trait attribute can be contained either in the defining object or in another object that is deferred to by the trait.
    
Notification: 
    Setting the value of a trait attribute can notify other parts of the program that the value has changed.
    
Visualization: 
    TBD - enaml?

#### Reduce codebase

* Traits is a huge project with **> 92,000** lines and **< %60** covered by unit-tests.
    
* Traity is a tiny project **< 2,000** lines and **> %95** covered by unit-tests.
    
Traity is designed to remain tiny kernel of stable code which add-ons and extension may be based on top of.

#### Extend the learning curve

It is my feeling that while traits may be a good learning tool for new scientists it's monolithic structure makes it very hard for an advanced programmer to do specialized things. 

Traity is designed from the ground up to be tiny and transparent. Separating event notification from static typing from other more specialized helpers.

#### Python 3

Just mentioning it here. Traity is Python 3 compliant.

### Highlights

```python

# Optional decorator does two things
# 1. Makes all vproperty's including `trait` picklable. 
# 2. Allows static listeners to be defined on a class.
@init_properties
# Notice that the foo class does not have to inherit from any hastraits base class.
class Foo(object):

    #attr1 may emit events like changes  
    attr1 = listenable()
    
    #vproperty is a type checking propery.  
    attr2 = vproperty(type=int)
    
    #traits is a subclass of listenable and vproperty
    attr3 = trait(type=float)
    
    def __init__(self):
        #Optional: Alows listenable and trait properties to emit events. 
        init_events(self)  
    
    @attr3.changed
    def notify(self, event):
        pass
```

#### Building back up to traits

As I mentioned before, this is meant to be a tiny implementation and extensions can be built on top if traity. 

Here is an example of how to re-create a simple HasTraits class from traity.

```python
class Int(trait):
    def __init__(default=0):
        trait.__init__(self, type=int, fdefault=lambda self:default)
    
    # Special method to allow trait to be called with or without parens '()'
    # Method __init_property__ is invoked when init_properties is called
    @classmethod
    def __init_property__(cls, owner, key):
       int_trait = cls()
       setattr(owner, key, int_trait)
       trait.__init_property__(int_trait, owner, key)
    
class HasTraitsMeta(type):
     def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        init_properties(cls)
        return cls
     
class HasTraits(object):
   __metaclass__ = HasTraitsMeta
   
   def __init__(**kwargs):
       self.__dict__.update(kwargs)
       init_events(self)
       
class MyObject(HasTraits):
    i = Int
    
obj = MyObject(i=1)
```

