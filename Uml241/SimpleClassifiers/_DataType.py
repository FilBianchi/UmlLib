from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Classifier import Classifier

class DataType(Classifier):
    """UML metaclass DataType."""
    __spec__ = SPECIFICATIONS['DataType']
    ownedAttribute: list[Property]
    ownedOperation: list[Operation]
    def inherit(self, *args, **kwargs):
        try:
            return _operation(self, 'DataType', 'inherit', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
