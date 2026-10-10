from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._Class import Class

class Component(Class):
    """UML metaclass Component."""
    __spec__ = SPECIFICATIONS['Component']
    isIndirectlyInstantiated: bool | None
    packagedElement: list[PackageableElement]
    provided: list[Interface]
    realization: list[ComponentRealization]
    required: list[Interface]
