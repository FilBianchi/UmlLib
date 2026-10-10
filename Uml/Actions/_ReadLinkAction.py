from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._LinkAction import LinkAction

class ReadLinkAction(LinkAction):
    """UML metaclass ReadLinkAction."""
    __spec__ = SPECIFICATIONS['ReadLinkAction']
    result: OutputPin | None
    def openEnd(self, *args, **kwargs):
        try:
            return _operation(self, 'ReadLinkAction', 'openEnd', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
