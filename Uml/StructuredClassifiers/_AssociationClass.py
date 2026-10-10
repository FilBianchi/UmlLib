from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._Class import Class
from ..StructuredClassifiers._Association import Association

class AssociationClass(Class, Association):
    """UML metaclass AssociationClass."""
    __spec__ = SPECIFICATIONS['AssociationClass']
