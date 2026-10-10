from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._ConnectableElement import ConnectableElement
from ..Deployments._DeploymentTarget import DeploymentTarget
from ..Classification._StructuralFeature import StructuralFeature

class Property(ConnectableElement, DeploymentTarget, StructuralFeature):
    """UML metaclass Property."""
    __spec__ = SPECIFICATIONS['Property']
    aggregation: AggregationKind | None
    association: Association | None
    associationEnd: Property | None
    class_: Class | None
    @property
    def class_(self):
        return getattr(self, 'class')
    @class_.setter
    def class_(self, value):
        setattr(self, 'class', value)
    datatype: DataType | None
    defaultValue: ValueSpecification | None
    interface: Interface | None
    isComposite: bool | None
    isDerived: bool | None
    isDerivedUnion: bool | None
    isID: bool | None
    opposite: Property | None
    owningAssociation: Association | None
    qualifier: list[Property]
    redefinedProperty: list[Property]
    subsettedProperty: list[Property]
    def isAttribute(self, *args, **kwargs):
        try:
            return _operation(self, 'Property', 'isAttribute', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isCompatibleWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Property', 'isCompatibleWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Property', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isNavigable(self, *args, **kwargs):
        try:
            return _operation(self, 'Property', 'isNavigable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def subsettingContext(self, *args, **kwargs):
        try:
            return _operation(self, 'Property', 'subsettingContext', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
