from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Deployments._Artifact import Artifact

class DeploymentSpecification(Artifact):
    """UML metaclass DeploymentSpecification."""
    __spec__ = SPECIFICATIONS['DeploymentSpecification']
    deployment: Deployment | None
    deploymentLocation: str | None
    executionLocation: str | None
