from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class LinkAction(Action):
    """UML metaclass LinkAction."""
    __spec__ = SPECIFICATIONS['LinkAction']
    endData: list[LinkEndData]
    inputValue: list[InputPin]
    def association(self, *args, **kwargs):
        try:
            return _operation(self, 'LinkAction', 'association', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
