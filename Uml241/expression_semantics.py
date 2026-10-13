"""Trusted expression facts for the isolated UML 2.4.1 backend."""
from ._runtime import engine
from importlib import import_module
_module=import_module(engine.__name__+'.expression_semantics')
ExpressionFacts=_module.ExpressionFacts
register_expression_facts=_module.register_expression_facts
expression_fact=_module.expression_fact
