from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteLinkAction import WriteLinkAction

class DestroyLinkAction(WriteLinkAction):
    """UML metaclass DestroyLinkAction."""
    __spec__ = SPECIFICATIONS['DestroyLinkAction']
    endData: list[LinkEndDestructionData]
