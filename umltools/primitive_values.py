"""Values of model-defined primitive types, identified by definition, never name aliases."""
from dataclasses import dataclass
from weakref import WeakKeyDictionary
import re
from .native import kind, NativeNotImplemented
from .contracts import validate_item
from .evaluation_context import profile_evaluation

STANDARD_NAMES = frozenset(('Boolean','Integer','Real','String','UnlimitedNatural'))
_codecs = WeakKeyDictionary()


@dataclass(frozen=True)
class PrimitiveCodec:
    decode: object
    encode: object
    validate: object


def _check_type(classifier):
    if not hasattr(classifier,'__registry__') or not kind(classifier,classifier,'PrimitiveType'):
        raise TypeError('Expected a UML PrimitiveType definition')
    classifier._ensure_alive()


def register_primitive_codec(classifier, *, decode, encode, validate):
    """Register trusted conversion/validation callbacks for this exact type object."""
    if profile_evaluation.get(): raise ValueError('Cannot change codecs during value evaluation')
    _check_type(classifier)
    if classifier.name in STANDARD_NAMES: raise ValueError('Standard primitive representations are built in')
    if not all(callable(f) for f in (decode,encode,validate)): raise TypeError('Codec callbacks must be callable')
    _codecs[classifier]=PrimitiveCodec(decode,encode,validate)


def unregister_primitive_codec(classifier):
    if profile_evaluation.get(): raise ValueError('Cannot change codecs during value evaluation')
    _codecs.pop(classifier,None)


def _evaluate(function,*args):
    token=profile_evaluation.set(True)
    try:
        try: return function(*args)
        except Exception as error: raise ValueError('Primitive codec callback failed') from error
    finally: profile_evaluation.reset(token)


def _decode_standard(classifier,lexical):
    name=classifier.name
    if name=='String': value=lexical
    elif name=='Boolean':
        if lexical not in ('true','false','1','0'): raise ValueError('Invalid Boolean lexical value')
        value=lexical in ('true','1')
    elif name in ('Integer','UnlimitedNatural'):
        if name=='UnlimitedNatural' and lexical.strip()=='*': value=float('inf')
        else:
            pattern=r'\+?[0-9]+' if name=='UnlimitedNatural' else r'[+-]?[0-9]+'
            if not re.fullmatch(pattern,lexical.strip()): raise ValueError('Invalid numeric lexical value')
            value=int(lexical)
    elif name=='Real': value=float(lexical)
    else: raise NativeNotImplemented('Primitive semantics require a registered codec')
    validate_item(classifier,value,name)
    return value


@dataclass(frozen=True)
class PrimitiveValue:
    """An immutable typed lexical value; unknown semantics do not erase its identity."""
    classifier: object
    lexical: str

    def __post_init__(self):
        _check_type(self.classifier)
        if type(self.lexical) is not str: raise TypeError('Primitive lexical value must be a string')
        if self.has_semantics: self.to_python()

    @property
    def has_semantics(self):
        self.classifier._ensure_alive()
        return self.classifier in _codecs or self.classifier.name in STANDARD_NAMES

    def to_python(self):
        self.classifier._ensure_alive()
        codec=_codecs.get(self.classifier)
        if codec is None: return _decode_standard(self.classifier,self.lexical)
        decoded=_evaluate(codec.decode,self.lexical)
        result=_evaluate(codec.validate,decoded)
        if type(result) is not bool: raise TypeError('Primitive validator must return an exact Boolean')
        if not result: raise ValueError('Primitive value violates the registered validator')
        return decoded

    @classmethod
    def from_python(cls,classifier,value):
        _check_type(classifier)
        codec=_codecs.get(classifier)
        if codec is None: raise NativeNotImplemented('Python conversion requires an explicitly registered codec')
        result=_evaluate(codec.validate,value)
        if type(result) is not bool: raise TypeError('Primitive validator must return an exact Boolean')
        if not result: raise ValueError('Primitive value violates the registered validator')
        lexical=_evaluate(codec.encode,value)
        if type(lexical) is not str: raise TypeError('Primitive encoder must return a string')
        instance=cls(classifier,lexical)
        # Validate the encoded representation too; encoders may not bypass decoders.
        instance.to_python()
        return instance

    def with_lexical(self,lexical): return type(self)(self.classifier,lexical)

    def validate(self):
        self.classifier._ensure_alive()
        try: self.to_python()
        except NativeNotImplemented: return [('unsupported primitive value','PrimitiveType.semantics')]
        except (ValueError,TypeError): return [('primitive value','PrimitiveType.value')]
        return []
