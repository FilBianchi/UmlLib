from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReplyAction(Action):
    """UML metaclass ReplyAction."""
    __spec__ = SPECIFICATIONS['ReplyAction']
    replyToCall: Trigger | None
    replyValue: list[InputPin]
    returnInformation: InputPin | None
