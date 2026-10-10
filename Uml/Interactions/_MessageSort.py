from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

class MessageSort(Enum):
    synchCall = 'synchCall'
    asynchCall = 'asynchCall'
    asynchSignal = 'asynchSignal'
    createMessage = 'createMessage'
    deleteMessage = 'deleteMessage'
    reply = 'reply'
