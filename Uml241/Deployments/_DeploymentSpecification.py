from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Deployments._Artifact import Artifact

class DeploymentSpecification(Artifact):
    """UML metaclass DeploymentSpecification."""
    __spec__ = SPECIFICATIONS['DeploymentSpecification']
    deployment: Deployment | None
    deploymentLocation: str | None
    executionLocation: str | None
