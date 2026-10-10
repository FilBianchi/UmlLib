from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
