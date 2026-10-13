from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class ProtocolConformance(DirectedRelationship):
    """UML metaclass ProtocolConformance."""
    __spec__ = SPECIFICATIONS['ProtocolConformance']
    generalMachine: ProtocolStateMachine | None
    specificMachine: ProtocolStateMachine | None
