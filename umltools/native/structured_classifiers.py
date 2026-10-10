"""Interfaces and connector derivations."""
from . import query, kind, unique, instances


def component_interfaces(self, provided):
    classifiers = [self] + self.allParents()
    realizers = unique(c for classifier in classifiers for r in getattr(classifier, 'realization', []) for c in r.realizingClassifier)
    realizers = unique(realizers + [p for c in realizers for p in c.allParents()])
    method = 'allRealizedInterfaces' if provided else 'allUsedInterfaces'
    port_property = 'provided' if provided else 'required'
    return unique(getattr(self, method)() + [i for c in realizers for i in getattr(c, method)()] + [i for c in classifiers for p in getattr(c, 'ownedPort', []) for i in getattr(p, port_property)])


@query('Component.provided')
def component_provided(self): return component_interfaces(self, True)


@query('Component.required')
def component_required(self): return component_interfaces(self, False)


@query('ConnectableElement.end')
def ends(self): return [end for end in instances(self, 'ConnectorEnd') if end.role is self]


@query('Connector.kind')
def connector_kind(self):
    delegation = any(kind(self, end.role, 'Port') and end.partWithPort is None and not end.role.isBehavior for end in self.end)
    return self.__registry__['ConnectorKind'].delegation if delegation else self.__registry__['ConnectorKind'].assembly


@query('ConnectorEnd.definingEnd')
def defining_end(self):
    connector = self.owner
    if not kind(self, connector, 'Connector'):
        connector = next((c for c in instances(self, 'Connector') if self in c.end), None)
    if connector is None: raise ValueError('ConnectorEnd has no connector')
    if connector.type is None: return None
    index = list(connector.end).index(self)
    if index >= len(connector.type.memberEnd): raise ValueError('Connector and association have different arities')
    return connector.type.memberEnd[index]


@query('Port.basicProvided')
def basic_provided(self):
    if kind(self, self.type, 'Interface'): return [self.type]
    if not kind(self, self.type, 'Classifier'): raise ValueError('Port requires a classifier type')
    return self.type.allRealizedInterfaces()


@query('Port.basicRequired')
def basic_required(self):
    if not kind(self, self.type, 'Classifier'): raise ValueError('Port requires a classifier type')
    return self.type.allUsedInterfaces()


@query('Port.provided')
def provided(self): return self.basicRequired() if self.isConjugated else self.basicProvided()


@query('Port.required')
def required(self): return self.basicProvided() if self.isConjugated else self.basicRequired()


@query('ProtocolTransition.referred')
def referred(self): return unique(t.event.operation for t in self.trigger if kind(self, t.event, 'CallEvent') and t.event.operation is not None)


@query('Transition.isConsistentWith')
def transition_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    if not kind(self, redefiningElement, 'Transition'): return False
    # Source text erroneously names Vertex::redefinedTransition; Vertex has redefinedVertex.
    if redefiningElement.source is None or self.source is None: raise ValueError('Transition requires a source')
    return self.source in self._items(redefiningElement.source.redefinedVertex)


@query('Vertex.isConsistentWith')
def vertex_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    if not kind(self, redefiningElement, 'Vertex'): return False
    owner = redefiningElement.owner
    if not kind(self, owner, 'RedefinableElement'): raise ValueError('Vertex owner must be redefinable')
    return self.owner in owner.redefinedElement
