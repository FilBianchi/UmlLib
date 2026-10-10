from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

class Element(UmlElement):
    """UML metaclass Element."""
    __spec__ = SPECIFICATIONS['Element']
    ownedComment: list[Comment]
    ownedElement: list[Element]
    owner: Element | None
    def allOwnedElements(self, *args, **kwargs):
        try:
            return _operation(self, 'Element', 'allOwnedElements', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def mustBeOwned(self, *args, **kwargs):
        try:
            return _operation(self, 'Element', 'mustBeOwned', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
