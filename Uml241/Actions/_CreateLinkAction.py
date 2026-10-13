from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteLinkAction import WriteLinkAction

class CreateLinkAction(WriteLinkAction):
    """UML metaclass CreateLinkAction."""
    __spec__ = SPECIFICATIONS['CreateLinkAction']
    endData: list[LinkEndCreationData]
