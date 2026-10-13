from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class ParameterableElement(Element):
    """UML metaclass ParameterableElement."""
    __spec__ = SPECIFICATIONS['ParameterableElement']
    owningTemplateParameter: TemplateParameter | None
    templateParameter: TemplateParameter | None
    def isCompatibleWith(self, *args, **kwargs):
        try:
            return _operation(self, 'ParameterableElement', 'isCompatibleWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isTemplateParameter(self, *args, **kwargs):
        try:
            return _operation(self, 'ParameterableElement', 'isTemplateParameter', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
