from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._RedefinableElement import RedefinableElement
from ..CommonStructure._TemplateSignature import TemplateSignature

class RedefinableTemplateSignature(RedefinableElement, TemplateSignature):
    """UML metaclass RedefinableTemplateSignature."""
    __spec__ = SPECIFICATIONS['RedefinableTemplateSignature']
    classifier: Classifier | None
    extendedSignature: list[RedefinableTemplateSignature]
    inheritedParameter: list[TemplateParameter]
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'RedefinableTemplateSignature', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
