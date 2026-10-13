"""Typed lexical primitives and trusted per-definition codecs for UML 2.4.1."""
from importlib import import_module
from ._runtime import engine
_module=import_module(engine.__name__+'.primitive_values')
PrimitiveValue=_module.PrimitiveValue
PrimitiveCodec=_module.PrimitiveCodec
register_primitive_codec=_module.register_primitive_codec
unregister_primitive_codec=_module.unregister_primitive_codec
