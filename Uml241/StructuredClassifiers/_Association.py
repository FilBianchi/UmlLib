from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Relationship import Relationship
from ..Classification._Classifier import Classifier

class Association(Relationship, Classifier):
    """UML metaclass Association."""
    __spec__ = SPECIFICATIONS['Association']
    endType: list[Type]
    isDerived: bool | None
    memberEnd: list[Property]
    navigableOwnedEnd: list[Property]
    ownedEnd: list[Property]
