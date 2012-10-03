## Traity

My ideal traits's like library.

traity.events + traity.statics == traity.traits.  

### Objectives

#### Uphold the main principles and philosophy of traits 

**Initialization:**
    A may optionally have a default value.
    
**Validation:**
    A trait attribute is explicitly typed. 
    The type of a trait-based attribute is evident in the code, and only values that meet a programmer-specified set of criteria (i.e., the trait definition) can be assigned to that attribute. 
    
**Deferral:**
    The value of a trait attribute can be contained either in the defining object or in another object that is deferred to by the trait.
    
**Notification:**
    Setting the value of a trait attribute can notify other parts of the program that the value has changed.
    
**Visualization:**
    TBD - enaml?

#### Reduce codebase

* Traits is a huge project with **> 92,000** lines and **< %60** covered by unit-tests.
    
* Traity is a tiny project **< 2,000** lines and **> %95** covered by unit-tests.
    * Traity's `event` framework is **< 400** lines of code without comments or doc-strings, and *completely independent* of any other framework.
    * Traity's `static` framework is **< 200** lines of code without comments or doc-strings, and *completely independent* of any other framework.
    * Traity's `traits` framework is **< 100** lines of code without comments or doc-strings, and combines `traity.events` and `traity.statics`
    
Traity is designed to remain tiny kernel of stable code which add-ons and extension may be based on top of.

#### Extend the learning curve

It is my feeling that while traits may be a good learning tool for new scientists it's monolithic structure makes it very hard for an advanced programmer to do specialized things. 

Traity is designed from the ground up to be tiny and transparent. Separating event notification from static typing from other more specialized helpers.

#### Python 3

Just mentioning it here. Traity is Python 3 compliant.

### Highlights

#### Basic syntax

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
    
    @attr3.changed()
    def notify(self, event):
        pass
```

#### Strong vs. Weak Delegation

Traity introduces a concept of strong delegation
```python

class Obj(object):
    attr1 = trait(instance=str)
    
    #Strong delegation to attr1.upper, Error checking at class creation.
    deleg = attr.upper
    
    #Weak delegation to attr1.upper, errors only caught when accessed.
    deleg2 = delegate('attr1', 'upper')
    
```


#### Strong vs. Weak Notification

```python

@init_properties
class Obj(object):
    attr1 = trait(instance=str)
    
    def __init__(self): init_events(self)
    
    #Strong Notification, attr1 *must* exists at class creation and be a litstenable trait.
    @attr1.changed()
    def hello(self, event):
        print "hello"

    #Weak Notification, attr1 may not even exist, or may be a typo. but no error will ever be raised
    @on_trait_changed('attr1')
    def hello(self, event):
        print "hello"

```
#### Dispatchers and global listeners

Global global listeners enable fine grained debugging capability.

```python

def print_change_events(event):
    if event.target[-1] == 'changed':
        print "event", event

with global_listener(print_change_events):
    ...

```

Custom dispatchers handle executing event listeners. A dispatcher is a callable object that accepts an
event and a listener as arguments.

Dispatchers may be added at three levels:

 * On the trait. The dispatcher has the highest priority, any listener watching this trait will be called by the dispatcher.
 * On the object. Any listener watching any trait on this object will be called by the dispatcher.
 * Globally. Any listener watching any trait will be called by the dispatcher.

##### Global and object dispatchers


```python

#Global dispatcher stores all events in the tocall list
with queue() as tocall: 
    #object dispatcher prevents all events on obj2 from being propagated
    with events(obj2).quiet():
        obj1.trait1 = 1
        obj2.trait1 = 1

assert len(tocall) == 1
```

##### Trait dispatchers

TODO: this is not implemented yet

```python

def my_function(event, handler):
    print "calling", handler
    handler(event)
     
@init_properties
class Obj(object):

    trait_attr = trait(type=float)
    
    def __init__(self):
        init_events(self)  
    
    @attr3.changed(dispatcher=my_function)
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

