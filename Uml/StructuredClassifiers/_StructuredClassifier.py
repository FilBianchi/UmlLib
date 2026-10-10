from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Classifier import Classifier

class StructuredClassifier(Classifier):
    """UML metaclass StructuredClassifier."""
    __spec__ = SPECIFICATIONS['StructuredClassifier']
    ownedAttribute: list[Property]
    ownedConnector: list[Connector]
    part: list[Property]
    role: list[ConnectableElement]
    def allRoles(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredClassifier', 'allRoles', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
