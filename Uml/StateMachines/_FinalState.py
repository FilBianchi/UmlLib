from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StateMachines._State import State

class FinalState(State):
    """UML metaclass FinalState."""
    __spec__ = SPECIFICATIONS['FinalState']
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'FinalState', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
