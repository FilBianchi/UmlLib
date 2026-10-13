"""Structured validation for the isolated UML 2.4.1 backend."""
from ._runtime import engine
from importlib import import_module
_validation = import_module(engine.__name__ + '.validation')
ValidationIssue = _validation.ValidationIssue
ValidationReport = _validation.ValidationReport
validate_element = _validation.validate_element
validate_document = _validation.validate_document
