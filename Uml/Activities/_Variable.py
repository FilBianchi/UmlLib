from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._ConnectableElement import ConnectableElement
from ..CommonStructure._MultiplicityElement import MultiplicityElement

class Variable(ConnectableElement, MultiplicityElement):
    """UML metaclass Variable."""
    __spec__ = SPECIFICATIONS['Variable']
    activityScope: Activity | None
    scope: StructuredActivityNode | None
    def isAccessibleBy(self, *args, **kwargs):
        try:
            return _operation(self, 'Variable', 'isAccessibleBy', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
