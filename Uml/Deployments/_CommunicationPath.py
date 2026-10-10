from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._Association import Association

class CommunicationPath(Association):
    """UML metaclass CommunicationPath."""
    __spec__ = SPECIFICATIONS['CommunicationPath']
