"""Trusted facts for UML 2.4.1 execution obligations outside model syntax."""
from importlib import import_module
from ._runtime import engine
_module=import_module(engine.__name__+'.semantic_facts')
register_semantic_facts=_module.register_semantic_facts
semantic_fact=_module.semantic_fact
