from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteLinkAction import WriteLinkAction

class CreateLinkAction(WriteLinkAction):
    """UML metaclass CreateLinkAction."""
    __spec__ = SPECIFICATIONS['CreateLinkAction']
    endData: list[LinkEndCreationData]
