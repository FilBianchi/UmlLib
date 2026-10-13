from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class ReplyAction(Action):
    """UML metaclass ReplyAction."""
    __spec__ = SPECIFICATIONS['ReplyAction']
    replyToCall: Trigger | None
    replyValue: list[InputPin]
    returnInformation: InputPin | None
