from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._InvocationAction import InvocationAction

class SendSignalAction(InvocationAction):
    """UML metaclass SendSignalAction."""
    __spec__ = SPECIFICATIONS['SendSignalAction']
    signal: Signal | None
    target: InputPin | None
