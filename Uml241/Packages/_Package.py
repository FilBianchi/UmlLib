from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._PackageableElement import PackageableElement
from ..CommonStructure._TemplateableElement import TemplateableElement
from ..CommonStructure._Namespace import Namespace

class Package(PackageableElement, TemplateableElement, Namespace):
    """UML metaclass Package."""
    __spec__ = SPECIFICATIONS['Package']
    URI: str | None
    nestedPackage: list[Package]
    nestingPackage: Package | None
    ownedStereotype: list[Stereotype]
    ownedType: list[Type]
    packageMerge: list[PackageMerge]
    packagedElement: list[PackageableElement]
    profileApplication: list[ProfileApplication]
    def allApplicableStereotypes(self, *args, **kwargs):
        try:
            return _operation(self, 'Package', 'allApplicableStereotypes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def containingProfile(self, *args, **kwargs):
        try:
            return _operation(self, 'Package', 'containingProfile', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def makesVisible(self, *args, **kwargs):
        try:
            return _operation(self, 'Package', 'makesVisible', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def mustBeOwned(self, *args, **kwargs):
        try:
            return _operation(self, 'Package', 'mustBeOwned', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def visibleMembers(self, *args, **kwargs):
        try:
            return _operation(self, 'Package', 'visibleMembers', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
