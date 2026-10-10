from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class ProtocolConformance(DirectedRelationship):
    """UML metaclass ProtocolConformance."""
    __spec__ = SPECIFICATIONS['ProtocolConformance']
    generalMachine: ProtocolStateMachine | None
    specificMachine: ProtocolStateMachine | None
