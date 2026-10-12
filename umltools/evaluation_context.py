"""Ordinary model/runtime writes are blocked during registered constraint checks."""
from contextvars import ContextVar
profile_evaluation = ContextVar('uml_profile_constraint_evaluation', default=False)
