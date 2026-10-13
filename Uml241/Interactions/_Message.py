from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class Message(NamedElement):
    """UML metaclass Message."""
    __spec__ = SPECIFICATIONS['Message']
    argument: list[ValueSpecification]
    connector: Connector | None
    interaction: Interaction | None
    messageKind: MessageKind | None
    messageSort: MessageSort | None
    receiveEvent: MessageEnd | None
    sendEvent: MessageEnd | None
    signature: NamedElement | None
