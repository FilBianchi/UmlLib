from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class TemplateableElement(Element):
    """UML metaclass TemplateableElement."""
    __spec__ = SPECIFICATIONS['TemplateableElement']
    ownedTemplateSignature: TemplateSignature | None
    templateBinding: list[TemplateBinding]
    def isTemplate(self, *args, **kwargs):
        try:
            return _operation(self, 'TemplateableElement', 'isTemplate', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def parameterableElements(self, *args, **kwargs):
        try:
            return _operation(self, 'TemplateableElement', 'parameterableElements', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
