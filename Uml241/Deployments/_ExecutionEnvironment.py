from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Deployments._Node import Node

class ExecutionEnvironment(Node):
    """UML metaclass ExecutionEnvironment."""
    __spec__ = SPECIFICATIONS['ExecutionEnvironment']
