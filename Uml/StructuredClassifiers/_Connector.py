from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Feature import Feature

class Connector(Feature):
    """UML metaclass Connector."""
    __spec__ = SPECIFICATIONS['Connector']
    contract: list[Behavior]
    end: list[ConnectorEnd]
    kind: ConnectorKind | None
    redefinedConnector: list[Connector]
    type: Association | None
