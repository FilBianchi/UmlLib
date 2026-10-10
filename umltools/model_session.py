"""Explicit extents isolate UML allInstances queries in applications and tests."""
from contextvars import ContextVar
from weakref import WeakSet


current_session = ContextVar('uml_model_session', default=None)


class ModelSession:
    """Construct models inside ``with ModelSession():`` to isolate their extent."""
    def __init__(self):
        self.elements = WeakSet()
        self._token = None

    def __enter__(self):
        if self._token is not None: raise RuntimeError('This session is already active')
        self._token = current_session.set(self)
        return self

    def __exit__(self, *exception):
        current_session.reset(self._token)
        self._token = None

