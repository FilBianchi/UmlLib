from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._InvocationAction import InvocationAction

class BroadcastSignalAction(InvocationAction):
    """UML metaclass BroadcastSignalAction."""
    __spec__ = SPECIFICATIONS['BroadcastSignalAction']
    signal: Signal | None
