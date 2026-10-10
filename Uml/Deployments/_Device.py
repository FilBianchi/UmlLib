from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Deployments._Node import Node

class Device(Node):
    """UML metaclass Device."""
    __spec__ = SPECIFICATIONS['Device']
