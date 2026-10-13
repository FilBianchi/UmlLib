from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteLinkAction import WriteLinkAction

class DestroyLinkAction(WriteLinkAction):
    """UML metaclass DestroyLinkAction."""
    __spec__ = SPECIFICATIONS['DestroyLinkAction']
    endData: list[LinkEndDestructionData]
