from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Deployments._Node import Node

class ExecutionEnvironment(Node):
    """UML metaclass ExecutionEnvironment."""
    __spec__ = SPECIFICATIONS['ExecutionEnvironment']
