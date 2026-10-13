"""UML 2.4.1 runtime stereotype applications and profile application/removal."""
from importlib import import_module
from ._runtime import engine
_module=import_module(engine.__name__+'.stereotypes')
apply_profile=_module.apply_profile
unapply_profile=_module.unapply_profile
apply_stereotype=_module.apply_stereotype
applications=_module.applications
available_profiles=_module.available_profiles
validate_applications=_module.validate_applications
StereotypeApplication=_module.StereotypeApplication
