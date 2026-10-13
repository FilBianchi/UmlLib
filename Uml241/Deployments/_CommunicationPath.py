from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._Association import Association

class CommunicationPath(Association):
    """UML metaclass CommunicationPath."""
    __spec__ = SPECIFICATIONS['CommunicationPath']
