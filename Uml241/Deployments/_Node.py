from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._Class import Class
from ..Deployments._DeploymentTarget import DeploymentTarget

class Node(Class, DeploymentTarget):
    """UML metaclass Node."""
    __spec__ = SPECIFICATIONS['Node']
    nestedNode: list[Node]
