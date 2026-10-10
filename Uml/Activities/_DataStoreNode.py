from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._CentralBufferNode import CentralBufferNode

class DataStoreNode(CentralBufferNode):
    """UML metaclass DataStoreNode."""
    __spec__ = SPECIFICATIONS['DataStoreNode']
