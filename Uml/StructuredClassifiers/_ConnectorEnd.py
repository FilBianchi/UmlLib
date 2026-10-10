from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._MultiplicityElement import MultiplicityElement

class ConnectorEnd(MultiplicityElement):
    """UML metaclass ConnectorEnd."""
    __spec__ = SPECIFICATIONS['ConnectorEnd']
    definingEnd: Property | None
    partWithPort: Property | None
    role: ConnectableElement | None
