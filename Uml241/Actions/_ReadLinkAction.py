from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._LinkAction import LinkAction

class ReadLinkAction(LinkAction):
    """UML metaclass ReadLinkAction."""
    __spec__ = SPECIFICATIONS['ReadLinkAction']
    result: OutputPin | None
