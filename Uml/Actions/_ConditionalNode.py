from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._StructuredActivityNode import StructuredActivityNode

class ConditionalNode(StructuredActivityNode):
    """UML metaclass ConditionalNode."""
    __spec__ = SPECIFICATIONS['ConditionalNode']
    clause: list[Clause]
    isAssured: bool | None
    isDeterminate: bool | None
    result: list[OutputPin]
    def allActions(self, *args, **kwargs):
        try:
            return _operation(self, 'ConditionalNode', 'allActions', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
