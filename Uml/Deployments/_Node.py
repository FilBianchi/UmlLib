from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._Class import Class
from ..Deployments._DeploymentTarget import DeploymentTarget

class Node(Class, DeploymentTarget):
    """UML metaclass Node."""
    __spec__ = SPECIFICATIONS['Node']
    nestedNode: list[Node]
