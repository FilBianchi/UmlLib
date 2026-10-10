from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ControlNode import ControlNode

class DecisionNode(ControlNode):
    """UML metaclass DecisionNode."""
    __spec__ = SPECIFICATIONS['DecisionNode']
    decisionInput: Behavior | None
    decisionInputFlow: ObjectFlow | None
