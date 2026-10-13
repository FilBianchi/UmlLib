from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._LinkAction import LinkAction

class WriteLinkAction(LinkAction):
    """UML metaclass WriteLinkAction."""
    __spec__ = SPECIFICATIONS['WriteLinkAction']
