from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation

class MessageSort(Enum):
    synchCall = 'synchCall'
    asynchCall = 'asynchCall'
    asynchSignal = 'asynchSignal'
    createMessage = 'createMessage'
    deleteMessage = 'deleteMessage'
    reply = 'reply'
