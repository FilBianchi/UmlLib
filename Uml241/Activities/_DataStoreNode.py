from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._CentralBufferNode import CentralBufferNode

class DataStoreNode(CentralBufferNode):
    """UML metaclass DataStoreNode."""
    __spec__ = SPECIFICATIONS['DataStoreNode']
