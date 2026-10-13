from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._TemplateableElement import TemplateableElement
from ..Values._Expression import Expression

class StringExpression(TemplateableElement, Expression):
    """UML metaclass StringExpression."""
    __spec__ = SPECIFICATIONS['StringExpression']
    owningExpression: StringExpression | None
    subExpression: list[StringExpression]
    def stringValue(self, *args, **kwargs):
        try:
            return _operation(self, 'StringExpression', 'stringValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
