from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._CreateLinkAction import CreateLinkAction

class CreateLinkObjectAction(CreateLinkAction):
    """UML metaclass CreateLinkObjectAction."""
    __spec__ = SPECIFICATIONS['CreateLinkObjectAction']
    result: OutputPin | None
