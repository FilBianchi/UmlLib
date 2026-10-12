"""Information-flow channels: UML 2.5.1 sections 20.1 and 20.2.

Classifier conformance is meaningful for typed ends; two different object/part
references are not interchangeable merely because they have the same type.
"""
from . import invariant, kind, instances, NativeNotImplemented
from .constraints_basic import required


def endpoint_conforms(self, source, channel):
    if source is channel: return True
    if kind(self, source, 'Classifier') and kind(self, channel, 'Classifier'):
        return source.conformsTo(channel)
    if kind(self, channel, 'Classifier'):
        if kind(self, source, 'TypedElement'):
            return kind(self, source.type, 'Classifier') and source.type.conformsTo(channel)
        if kind(self, source, 'InstanceSpecification'):
            return any(c.conformsTo(channel) for c in source.classifier)
    if kind(self, source, 'Classifier') and kind(self, channel, 'TypedElement'):
        return kind(self, channel.type, 'Classifier') and source.conformsTo(channel.type)
    return False


def side_matches(self, endpoints, channel):
    return bool(endpoints) and bool(channel) and all(any(endpoint_conforms(self, e, c) for c in channel) for e in endpoints)


def directed_matches(self, sources, targets, a, b, reversible=False):
    return (side_matches(self, sources, a) and side_matches(self, targets, b) or
            reversible and side_matches(self, sources, b) and side_matches(self, targets, a))


def connector_matches(self, connector, sources, targets):
    ends = list(connector.end)
    def candidates(end):
        # partWithPort identifies the part on which a connected port resides.
        return [e for e in (end.role, end.partWithPort) if e is not None]
    return undirected_matches(self, sources, targets, [candidates(end) for end in ends])


def undirected_matches(self, sources, targets, ends):
    """Partition channel ends into nonoverlapping source and target sides."""
    if not sources or not targets or len(ends) < 2: return False
    def options(endpoints):
        return [{i for i, values in enumerate(ends) if any(endpoint_conforms(self, endpoint, value) for value in values)} for endpoint in endpoints]
    source_options, target_options = options(sources), options(targets)
    if any(not option for option in source_options + target_options): return False
    source_options.sort(key=len)
    def assign(index, selected):
        if any(not option - selected for option in target_options): return False
        if index == len(source_options): return True
        option = source_options[index]
        if option & selected: return assign(index + 1, selected)
        return any(assign(index + 1, selected | {choice}) for choice in option)
    return assign(0, set())


def message_endpoints(self, end):
    if end is None:
        raise NativeNotImplemented('An external lost/found message end has no modeled endpoint')
    if kind(self, end, 'MessageOccurrenceSpecification'):
        return [required(required(end.covered).represents)]
    if kind(self, end, 'Gate'):
        message = required(end.message)
        mapping = getattr(message, '_gate_endpoint_bindings', {})
        if end in mapping: return [mapping[end]]
        raise NativeNotImplemented('A gate endpoint requires an explicit boundary-to-part mapping')
    raise ValueError('Unsupported kind of MessageEnd')


@invariant('InformationFlow.must_conform')
def realization_endpoints(self):
    sources, targets = list(self.informationSource), list(self.informationTarget)
    if not sources or not targets: return False
    for relationship in self.realization:
        if kind(self, relationship, 'DirectedRelationship'):
            if not directed_matches(self, sources, targets, relationship.source, relationship.target, True): return False
        elif kind(self, relationship, 'Association'):
            ends = list(relationship.memberEnd)
            if not undirected_matches(self, sources, targets, [[required(end.type)] for end in ends]): return False
        else:
            raise NativeNotImplemented('The realizing relationship has no supported channel ends')
    for edge in self.realizingActivityEdge:
        if not directed_matches(self, sources, targets, [required(edge.source)], [required(edge.target)]): return False
    for connector in self.realizingConnector:
        if not connector_matches(self, connector, sources, targets): return False
    for message in self.realizingMessage:
        if not directed_matches(self, sources, targets, message_endpoints(self, message.sendEvent),
                                message_endpoints(self, message.receiveEvent)): return False
    return True


@invariant('InformationItem.has_no')
def information_item_structure(self):
    return (not self.generalization and not self.feature and
            not any(any(e.type is self for e in a.memberEnd) for a in instances(self, 'Association')))


@invariant('InformationItem.not_instantiable')
def information_item_instances(self):
    return bool(self.isAbstract) and not any(self in instance.classifier for instance in instances(self, 'InstanceSpecification'))
