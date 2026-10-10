from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
    def isDistinguishableFrom(self, *args, **kwargs):
        try:
            return _operation(self, 'Message', 'isDistinguishableFrom', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
