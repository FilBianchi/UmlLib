"""Isolated instances and typed tags of UML 2.4.1 profile-defined types."""
from importlib import import_module
from ._runtime import engine
_module=import_module(engine.__name__+'.profile_values')
ProfileObject=_module.ProfileObject
EnumValue=_module.EnumValue
register_profile_constraint=_module.register_profile_constraint
unregister_profile_constraint=_module.unregister_profile_constraint
