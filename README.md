## Traity


My ideal traits's like library. 

traity.events + traity.statics == traity.traits.  



### Highlights

```python



# Optional decorator does two things
# 1. Makes all vproperty's including `trait` picklable. 
# 2. Allows static listeners to be defined on a class.
@init_properties
# Notice that the foo class does not have to inhrit from any hastraits base class.
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
    
```

