from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Feature import Feature

class Connector(Feature):
    """UML metaclass Connector."""
    __spec__ = SPECIFICATIONS['Connector']
    contract: list[Behavior]
    end: list[ConnectorEnd]
    kind: ConnectorKind | None
    redefinedConnector: list[Connector]
    type: Association | None
