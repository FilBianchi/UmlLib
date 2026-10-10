from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._LinkAction import LinkAction

class WriteLinkAction(LinkAction):
    """UML metaclass WriteLinkAction."""
    __spec__ = SPECIFICATIONS['WriteLinkAction']
