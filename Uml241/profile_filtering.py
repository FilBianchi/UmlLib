"""UML 2.4.1 strict profile availability views and checked element creation."""
from importlib import import_module
from ._runtime import engine
_module=import_module(engine.__name__+'.profile_filtering')
is_metaclass_available=_module.is_metaclass_available
is_element_available=_module.is_element_available
create_profiled_element=_module.create_profiled_element
validate_strict_profiles=_module.validate_strict_profiles
