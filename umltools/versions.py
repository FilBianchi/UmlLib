"""Version attribution is separate from transport namespaces and validation semantics."""
from dataclasses import dataclass, field

SEMANTIC_VERSION='2.5.1'


@dataclass(frozen=True)
class SourceDialect:
    namespace: str
    format: str
    possible_versions: tuple
    semantic_version: str = field(default_factory=lambda: SEMANTIC_VERSION)
    support: str = 'represented features only'


def describe_namespace(namespace):
    versions={
        'http://www.omg.org/spec/UML/20161101':('2.5.1',),
        # The vendored 2.5.1 normative metamodel itself still declares 20131001.
        'http://www.omg.org/spec/UML/20131001':('2.5','2.5.1'),
        'http://www.omg.org/spec/UML/20110701':('2.4.1',),
        'http://www.omg.org/spec/UML/20100901':('2.4','2.4.1'),
        'http://www.omg.org/spec/UML/20090901':('2.3',),
    }
    if namespace in versions: return SourceDialect(namespace,'OMG UML',versions[namespace])
    if namespace.startswith('http://www.eclipse.org/uml2/'):
        return SourceDialect(namespace,'Eclipse UML2',())
    raise ValueError('Unknown UML namespace')


def require_target_version(version):
    if version!=SEMANTIC_VERSION:
        from .xmi import XmiUnsupportedError
        raise XmiUnsupportedError('Version-specific export is not implemented for UML '+str(version)+
                                  '; changing a namespace does not convert metamodel semantics')
