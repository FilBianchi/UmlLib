from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._MultiplicityElement import MultiplicityElement

class ConnectorEnd(MultiplicityElement):
    """UML metaclass ConnectorEnd."""
    __spec__ = SPECIFICATIONS['ConnectorEnd']
    definingEnd: Property | None
    partWithPort: Property | None
    role: ConnectableElement | None
