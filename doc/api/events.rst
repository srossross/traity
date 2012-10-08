Events
================================================================================


.. automodule:: traity.events

    
    Event Objects
    --------------------
    
    .. autoclass:: traity.events.Event
        :members: target, dispatch

    Snitch Objects
    --------------------

    .. autoclass:: traity.events.Snitch
        :members: etrigger, trigger, quiet, queue, unique, listen, unlisten
        
    Functions
    -------------------
    
    .. autofunction:: connect
    .. autofunction:: disconnect
    .. autofunction:: connected
    .. autofunction:: events
    .. autofunction:: init_events
    .. autofunction:: init_events


    Global liteners
    --------------------

    .. autofunction:: add_global_listener
    .. autofunction:: remove_global_listener
    .. autofunction:: global_listener

    Global dispatchers 
    --------------------

    .. autofunction:: add_global_dispatcher    
    .. autofunction:: pop_global_dispatcher
    .. autofunction:: remove_global_dispatcher
    .. autofunction:: global_dispatcher
    .. autofunction:: quiet
    .. autofunction:: queue
    .. autofunction:: unique
    
