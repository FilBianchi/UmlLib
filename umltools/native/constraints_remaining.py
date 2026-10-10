"""Profiles, information flows and constraints expressed in prose by OMG."""
from . import invariant, kind, instances, reverse, single, NativeNotImplemented
from .constraints_basic import predicates, required, enum
from .constraints_actions import primitive
from .constraints_interactions import fragments, lifeline_equal, interaction_of


def base_properties(self):
    return [p for p in self.ownedAttribute if kind(self, p.association, 'Extension')]


def expression_fact(value, name):
    from ..expression_semantics import expression_fact as fact
    return fact(value, name)


predicates({
    'CollaborationUse.every_role': lambda s: all(any(role in b.supplier for b in s.roleBinding) for role in required(s.type).collaborationRole),
    'Profile.metaclass_reference_not_specialized': lambda s: all(s not in [p.namespace for p in c.allParents()] for imp in s.metaclassReference for c in s._items(imp.importedElement) if kind(s, c, 'Classifier')) and all(p not in [i.importedElement for i in s.metaclassReference] for c in s.packagedElement if kind(s, c, 'Classifier') for p in c.allParents()),
    'Profile.references_same_metamodel': lambda s: bool([p for ref in s.metamodelReference for imp in required(ref.importedPackage).elementImport for p in s._items(required(imp.importedElement).allOwningPackages())] + [p for ref in s.metaclassReference for p in s._items(required(ref.importedElement).allOwningPackages())]),
    'Stereotype.base_property_upper_bound': lambda s: all(p.upperBound() == 1 for p in base_properties(s)),
    'Stereotype.base_property_multiplicity_single_extension': lambda s: len(base_properties(s)) != 1 or base_properties(s)[0].is_(1, 1),
    'Stereotype.base_property_multiplicity_multiple_extension': lambda s: len(base_properties(s)) <= 1 or all(p.is_(0, 1) for p in base_properties(s)),
    'InformationFlow.convey_classifiers': lambda s: all(any(kind(s, c, name) for name in ('Class', 'Interface', 'InformationItem', 'Signal', 'Component')) for c in s.conveyed),
    'InformationItem.has_no': lambda s: not s.generalization and not s.feature,
    'InformationItem.not_instantiable': lambda s: bool(s.isAbstract),
    'Constraint.boolean_value': lambda s: kind(s, s.specification, 'LiteralBoolean') or primitive(required(s.specification).type, 'Boolean'),
    'Constraint.no_side_effects': lambda s: expression_fact(required(s.specification), 'pure'),
    'MultiplicityElement.value_specification_no_side_effects': lambda s: all(expression_fact(v, 'pure') for v in (s.lowerValue, s.upperValue) if v is not None),
    'MultiplicityElement.value_specification_constant': lambda s: all(expression_fact(v, 'constant') for v in (s.lowerValue, s.upperValue) if v is not None),
})


@invariant('Stereotype.name_not_clash')
def stereotype_keyword(self):
    # The standard keywords are metaclass names with an initial lower-case letter.
    extended = [p.type for p in base_properties(self) if kind(self, p.type, 'Class')]
    keywords = {c.name[:1].lower() + c.name[1:] for c in extended if c.name is not None}
    return self.name not in keywords


@invariant('ParameterSet.input')
def parameter_set_inputs(self):
    feature = self.owner
    if not kind(self, feature, 'BehavioralFeature'): return True
    return all(all(p.isStream for p in feature.ownedParameter if enum(p.direction) == direction and not p.parameterSet) for direction in ('in', 'out') if any(enum(p.direction) == direction for p in self.parameter))


@invariant('ParameterSet.two_parameter_sets')
def different_parameter_sets(self):
    for parameter in self.parameter:
        sets = parameter.parameterSet
        for a in sets:
            for b in sets:
                if a is not b and len(a.parameter) == len(b.parameter) and set(a.parameter) <= set(b.parameter): return False
    return True


@invariant('CollaborationUse.client_elements')
def collaboration_clients(self):
    clients = [c for b in self.roleBinding for c in b.client]
    suppliers = [c for b in self.roleBinding for c in b.supplier]
    if not all(kind(self, c, 'ConnectableElement') for c in clients + suppliers): return False
    client_owners = {c.owner for c in clients}
    supplier_owners = {c.owner for c in suppliers}
    return len(client_owners) <= 1 and len(supplier_owners) <= 1 and all(kind(self, c, 'StructuredClassifier') for c in client_owners) and all(kind(self, c, 'Collaboration') for c in supplier_owners)


@invariant('CollaborationUse.connectors')
def collaboration_connectors(self):
    for connector in required(self.type).ownedConnector:
        roles = {e.role for e in connector.end}
        bindings = [b for b in self.roleBinding if roles & set(b.supplier)]
        bound = {c for b in bindings for c in b.client}
        if not bound: return False
        owners = {c.owner for c in bound}
        if len(owners) != 1: return False
        owner = required(next(iter(owners)))
        if not kind(self, owner, 'StructuredClassifier'): return False
        if not any(all(e.role in bound for e in c.end) and (connector.type is None or c.type is None or connector.type.conformsTo(c.type)) for c in owner.ownedConnector): return False
    return True


@invariant('InformationFlow.sources_and_targets_kind')
def flow_endpoint_kinds(self):
    allowed = ('Actor', 'Node', 'UseCase', 'Artifact', 'Class', 'Component', 'Port', 'Property', 'Interface', 'Package', 'ActivityNode', 'ActivityPartition')
    return all(any(kind(self, e, n) for n in allowed) or kind(self, e, 'InstanceSpecification') and not any(kind(self, c, 'Relationship') for c in e.classifier) for e in list(self.informationSource) + list(self.informationTarget))


@invariant('InformationItem.sources_and_targets')
def information_item_endpoints(self):
    if not all(any(kind(self, c, n) for n in ('Class', 'Interface', 'InformationItem', 'Signal', 'Component')) for c in self.represented): return False
    flows = reverse(self, 'InformationFlow', 'conveyed')
    sources, targets = {e for f in flows for e in f.source}, {e for f in flows for e in f.target}
    return all(set(f.source) <= sources and set(f.target) <= targets for item in self.represented if kind(self, item, 'InformationItem') for f in reverse(item, 'InformationFlow', 'conveyed'))


@invariant('InformationFlow.must_conform')
def realization_endpoints(self):
    sources, targets = set(self.informationSource), set(self.informationTarget)
    for relationship in self.realization:
        if kind(self, relationship, 'DirectedRelationship'):
            a, b = set(relationship.source), set(relationship.target)
        elif kind(self, relationship, 'Association'):
            ends = relationship.memberEnd
            if len(ends) != 2: return False
            a, b = {ends[0].type}, {ends[1].type}
        else: raise NativeNotImplemented('Relationship has no directional realization semantics')
        if not (sources <= a and targets <= b or sources <= b and targets <= a): return False
    for edge in self.realizingActivityEdge:
        if edge.source not in sources or edge.target not in targets: return False
    for connector in self.realizingConnector:
        roles = {e.role for e in connector.end}
        if not sources | targets <= roles: return False
    for message in self.realizingMessage:
        if message.sendEvent is None or message.receiveEvent is None: return False
        a = required(message.sendEvent.covered).represents
        b = required(message.receiveEvent.covered).represents
        if a not in sources or b not in targets: return False
    return True


@invariant('ReduceAction.input_type_is_collection')
def collection_input(self):
    pin = required(self.collection)
    # UML represents token collections directly by a multivalued pin. A single
    # token may instead carry a domain-specific collection type.
    if pin.isMultivalued(): return True
    from ..expression_semantics import is_collection_type
    type_ = required(pin.type)
    if is_collection_type(type_): return True
    raise NativeNotImplemented('Single-token domain collection type requires a collection type adapter')


def decomposition_pairs(self, lifeline):
    original = [f for f in required(lifeline.interaction).fragment if lifeline in f._items(f.covered) and any(kind(self, f, n) for n in ('CombinedFragment', 'InteractionUse', 'OccurrenceSpecification'))]
    decomposed = [f for f in required(self.refersTo).fragment if kind(self, f, 'CombinedFragment') or kind(self, f, 'InteractionUse')]
    constructs = [f for f in original if not kind(self, f, 'OccurrenceSpecification')]
    if len(constructs) != len(decomposed): return None
    pairs = list(zip(constructs, decomposed))
    for a, b in pairs:
        if kind(self, a, 'CombinedFragment'):
            if not kind(self, b, 'CombinedFragment') or a.interactionOperator != b.interactionOperator or len(a.operand) != len(b.operand) or set(b.covered) != set(self.refersTo.lifeline): return None
        elif not kind(self, b, 'InteractionUse') or set(b.covered) != set(self.refersTo.lifeline): return None
    for occurrence in original:
        if not kind(self, occurrence, 'OccurrenceSpecification'): continue
        if not kind(self, occurrence, 'MessageOccurrenceSpecification'):
            raise NativeNotImplemented('Non-message decomposition occurrence requires a mapping to its actual gate')
        message = required(occurrence.message)
        outgoing = occurrence.isSend()
        name = ('out_' if outgoing else 'in_') + required(message.name)
        candidates = [g for g in self.refersTo.formalGate if g.getName() == name and required(g.message).signature is message.signature and g.message.messageSort == message.messageSort and (g.isReceive() if outgoing else g.isSend())]
        if len(candidates) != 1: return None
    return pairs


@invariant('PartDecomposition.assume')
def decomposition_structure(self):
    return all(decomposition_pairs(self, l) is not None for l in reverse(self, 'Lifeline', 'decomposedAs'))


@invariant('PartDecomposition.commutativity_of_decomposition')
def decomposition_commutes(self):
    for lifeline in reverse(self, 'Lifeline', 'decomposedAs'):
        pairs = decomposition_pairs(self, lifeline)
        if pairs is None: return False
        for original, counterpart in pairs:
            if not kind(self, original, 'InteractionUse'): continue
            matching = [l for l in required(original.refersTo).lifeline if lifeline_equal(l, lifeline)]
            if len(matching) != 1 or matching[0].decomposedAs is None or matching[0].decomposedAs.refersTo is not counterpart.refersTo: return False
    return True
