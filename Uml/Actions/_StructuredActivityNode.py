from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Namespace import Namespace
from ..Activities._ActivityGroup import ActivityGroup
from ..Actions._Action import Action

class StructuredActivityNode(Namespace, ActivityGroup, Action):
    """UML metaclass StructuredActivityNode."""
    __spec__ = SPECIFICATIONS['StructuredActivityNode']
    activity: Activity | None
    edge: list[ActivityEdge]
    mustIsolate: bool | None
    node: list[ActivityNode]
    structuredNodeInput: list[InputPin]
    structuredNodeOutput: list[OutputPin]
    variable: list[Variable]
    def allActions(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredActivityNode', 'allActions', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def allOwnedNodes(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredActivityNode', 'allOwnedNodes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def sourceNodes(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredActivityNode', 'sourceNodes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def targetNodes(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredActivityNode', 'targetNodes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def containingActivity(self, *args, **kwargs):
        try:
            return _operation(self, 'StructuredActivityNode', 'containingActivity', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
