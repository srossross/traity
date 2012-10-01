============================================
A comparison of traity with traits
============================================


I propose traity as a new base for 

Separation of "Notifications" from "Validation"
=================================================


Dynamically static attributes
======================================
  
Use static typing and validation ONLY when you need it. 
Instance properties are not defined in Python! so as a general guideline, 
we can separate this into a new and separate functionality. 

.. see:: :mod:`traity.tools.instance_properties`_

This will work even for simple python built-in `property` objects::

    from traity.tools.instance_properties import iobject, set_iproperty
    
    class Obj(iobject):
        pass
    
    def get_x(this):
       return 1
        
    set_iproperty(obj, 'x', property(get_x))
    
    print obj.x

  
String parser for on_trait_change 
======================================

* There is no validation for typos. 
* Why use a parser for  `'a,b,d:d'`?

traity::

   @a.assign
   @b.assign
   @d.d.assign
   def whatever_name_you_want():
       pass

or ::
    
    on_trait_change(obj, ('a', 'b', 'c'), handler)
    

Name mangling to call python classes
======================================

This is confusing and not Pythonic. By using decorators Python will natively give
you name errors when objects are not defined::

    class Foo(HasTraits):
        x = Any()
        #Error should be _x_changed - this type of typo is hard to track down. 
        def _y_changed(self, obj):
            pass

A more discriptive way::

    class Foo(object):

            x = trait()
    
            @x.change
            def any_name(self, event):
                pass


Interfaces
=============================================

Just use Python's ABC. This is code bloat and should be deprecated. 

Lists
==================================================

When using list traits an assignment to a list **always** results in a copy. 
This is not intuitive. Separating

HasTraits instance methods 
======================================

Too many! Lets hide these to the end user. traity uses the `events` method to get the `HasTraitsInstance Methods`::

    HasTraits.<tab>

    HasTraits.add_class_trait             HasTraits.clone_traits                HasTraits.remove_listener             HasTraits.trait_property_changed
    HasTraits.add_listener                HasTraits.configure_traits            HasTraits.remove_trait                HasTraits.trait_set
    HasTraits.add_trait                   HasTraits.copy_traits                 HasTraits.remove_trait_listener       HasTraits.trait_setq
    HasTraits.add_trait_category          HasTraits.copyable_trait_names        HasTraits.reset_traits                HasTraits.trait_subclasses
    HasTraits.add_trait_listener          HasTraits.default_traits_view         HasTraits.set                         HasTraits.trait_view
    HasTraits.all_trait_names             HasTraits.edit_traits                 HasTraits.set_trait_dispatch_handle   HasTraits.trait_view_elements
    HasTraits.base_trait                  HasTraits.editable_traits             HasTraits.sync_trait                  HasTraits.trait_views
    HasTraits.class_default_traits_view   HasTraits.get                         HasTraits.trait                       HasTraits.traits
    HasTraits.class_editable_traits       HasTraits.has_traits_interface        HasTraits.trait_context               HasTraits.traits_init
    HasTraits.class_trait_names           HasTraits.mro                         HasTraits.trait_get                   HasTraits.traits_inited
    HasTraits.class_trait_view            HasTraits.on_trait_change             HasTraits.trait_items_event           HasTraits.validate_trait
    HasTraits.class_trait_view_elements   HasTraits.on_trait_event              HasTraits.trait_monitor               HasTraits.wrappers
    HasTraits.class_traits                HasTraits.print_traits                HasTraits.trait_names                 asdf

traity does not even require a class that has traits to be a sub-class of hastraits::

    class Obj(any_base):
    
        x = trait()
        
        #Only required if you want traits to be listenable.
        def __init__(self): init_events(self)
        
    #Only required if you want traits to be pickelable and/or has statically defined @change listeners.
    init_properties(Obj)


HasTraits Metaclass bases
======================================

Every once in a great while integrating traits with another package whit Metaclasses can be a pain. traity only requires an optional class decorator. 
and this has no conflicts with any object Metaclass.


Consistency
=================================================

`Int` and `Int()` are not the same. The logic to do this should be an added functionality (if that) not an inseparable component. 

Attribute-specific Handler Signatures
=================================================

The core of traits uses introspection to determine how to call an event handler. 

    * _name_changed()
    * _name_changed(new)
    * _name_changed(old, new)
    * _name_changed(name, old, new)

The core of `traity.events` only allows one function signature. `_name_changed(event)`

Restricting the attributes on classes
======================================

Python 




