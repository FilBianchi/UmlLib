from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Feature import Feature
from ..CommonStructure._Namespace import Namespace

class BehavioralFeature(Feature, Namespace):
    """UML metaclass BehavioralFeature."""
    __spec__ = SPECIFICATIONS['BehavioralFeature']
    concurrency: CallConcurrencyKind | None
    isAbstract: bool | None
    method: list[Behavior]
    ownedParameter: list[Parameter]
    ownedParameterSet: list[ParameterSet]
    raisedException: list[Type]
    def isDistinguishableFrom(self, *args, **kwargs):
        try:
            return _operation(self, 'BehavioralFeature', 'isDistinguishableFrom', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'BehavioralFeature', 'inputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def outputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'BehavioralFeature', 'outputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
