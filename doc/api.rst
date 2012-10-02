================================================================================
traity's API
================================================================================


.. automodule:: traity
    :members: 

.. automodule:: traity.events
    :members: connect, disconnect, events, init_events, add_global_listener, remove_global_listener, global_listener
    
    
    .. autoclass:: traity.events.Event
        :members: target, dispatch

    .. autoclass:: traity.events.Snitch
        :members: etrigger, trigger, quiet, queue, unique, listen, unlisten
        

    Global dispatchers 
    --------------------
    
    .. autofunction:: quiet
    .. autofunction:: queue
    .. autofunction:: unique
    
    
    
.. automodule:: traity.statics
    :members: vproperty, delegate
    
.. automodule:: traity.tools.initializable_property
    :members: init_properties, persistent_property
    
.. automodule:: traity.tools.instance_properties
    :members: set_iproperty, get_iproperty, iobject
    
.. automodule:: traity.traits
    :members: trait
    
    
    
