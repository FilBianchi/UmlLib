from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Namespace import Namespace
from ..CommonStructure._Type import Type
from ..CommonStructure._TemplateableElement import TemplateableElement
from ..Classification._RedefinableElement import RedefinableElement

class Classifier(Namespace, Type, TemplateableElement, RedefinableElement):
    """UML metaclass Classifier."""
    __spec__ = SPECIFICATIONS['Classifier']
    attribute: list[Property]
    collaborationUse: list[CollaborationUse]
    feature: list[Feature]
    general: list[Classifier]
    generalization: list[Generalization]
    inheritedMember: list[NamedElement]
    isAbstract: bool | None
    isFinalSpecialization: bool | None
    ownedTemplateSignature: RedefinableTemplateSignature | None
    ownedUseCase: list[UseCase]
    powertypeExtent: list[GeneralizationSet]
    redefinedClassifier: list[Classifier]
    representation: CollaborationUse | None
    substitution: list[Substitution]
    templateParameter: ClassifierTemplateParameter | None
    useCase: list[UseCase]
    def allFeatures(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'allFeatures', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def allParents(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'allParents', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def conformsTo(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'conformsTo', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def hasVisibilityOf(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'hasVisibilityOf', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inherit(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'inherit', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inheritableMembers(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'inheritableMembers', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isTemplate(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'isTemplate', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def maySpecializeType(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'maySpecializeType', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def parents(self, *args, **kwargs):
        try:
            return _operation(self, 'Classifier', 'parents', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
