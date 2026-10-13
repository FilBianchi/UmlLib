from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation

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
