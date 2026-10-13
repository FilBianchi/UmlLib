from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._CreateLinkAction import CreateLinkAction

class CreateLinkObjectAction(CreateLinkAction):
    """UML metaclass CreateLinkObjectAction."""
    __spec__ = SPECIFICATIONS['CreateLinkObjectAction']
    result: OutputPin | None
