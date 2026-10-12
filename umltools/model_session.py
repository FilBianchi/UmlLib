"""Explicit extents isolate UML allInstances queries in applications and tests."""
from contextvars import ContextVar


current_session = ContextVar('uml_model_session', default=None)


class ModelSession:
    """Isolate and retain a logical extent until elements are explicitly deleted.

    Leaving the context changes the construction scope, not element lifetime.
    """
    def __init__(self):
        self.elements = set()
        self._token = None

    def __enter__(self):
        if self._token is not None: raise RuntimeError('This session is already active')
        self._token = current_session.set(self)
        return self

    def __exit__(self, *exception):
        current_session.reset(self._token)
        self._token = None

