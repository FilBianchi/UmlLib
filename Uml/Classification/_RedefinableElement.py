from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class RedefinableElement(NamedElement):
    """UML metaclass RedefinableElement."""
    __spec__ = SPECIFICATIONS['RedefinableElement']
    isLeaf: bool | None
    redefinedElement: list[RedefinableElement]
    redefinitionContext: list[Classifier]
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'RedefinableElement', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isRedefinitionContextValid(self, *args, **kwargs):
        try:
            return _operation(self, 'RedefinableElement', 'isRedefinitionContextValid', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
