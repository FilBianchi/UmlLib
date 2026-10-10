from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TemplateableElement import TemplateableElement
from ..CommonStructure._ParameterableElement import ParameterableElement
from ..Classification._BehavioralFeature import BehavioralFeature

class Operation(TemplateableElement, ParameterableElement, BehavioralFeature):
    """UML metaclass Operation."""
    __spec__ = SPECIFICATIONS['Operation']
    bodyCondition: Constraint | None
    class_: Class | None
    @property
    def class_(self):
        return getattr(self, 'class')
    @class_.setter
    def class_(self, value):
        setattr(self, 'class', value)
    datatype: DataType | None
    interface: Interface | None
    isOrdered: bool | None
    isQuery: bool | None
    isUnique: bool | None
    lower: int | None
    ownedParameter: list[Parameter]
    postcondition: list[Constraint]
    precondition: list[Constraint]
    raisedException: list[Type]
    redefinedOperation: list[Operation]
    templateParameter: OperationTemplateParameter | None
    type: Type | None
    upper: int | None
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Operation', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def returnResult(self, *args, **kwargs):
        try:
            return _operation(self, 'Operation', 'returnResult', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
