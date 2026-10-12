"""Profiles, information flows and constraints expressed in prose by OMG."""
from . import invariant, kind, instances, reverse, single, NativeNotImplemented
from .constraints_basic import predicates, required, enum
from .constraints_actions import primitive
from .constraints_interactions import fragments, lifeline_equal, interaction_of


def base_properties(self):
    return [p for p in self.allAttributes() if kind(self, p.association, 'Extension')]


def expression_fact(value, name):
    from ..expression_semantics import expression_fact as fact
    return fact(value, name)


predicates({
    'CollaborationUse.every_role': lambda s: all(any(role in b.supplier for b in s.roleBinding) for role in required(s.type).collaborationRole),
    'Profile.metaclass_reference_not_specialized': lambda s: all(s not in [p.namespace for p in c.allParents()] for imp in s.metaclassReference for c in s._items(imp.importedElement) if kind(s, c, 'Classifier')) and all(p not in [i.importedElement for i in s.metaclassReference] for c in s.packagedElement if kind(s, c, 'Classifier') for p in c.allParents()),
    'Stereotype.base_property_upper_bound': lambda s: all(p.upperBound() == 1 for p in base_properties(s)),
    'Stereotype.base_property_multiplicity_single_extension': lambda s: len(base_properties(s)) != 1 or base_properties(s)[0].is_(1, 1),
    'Stereotype.base_property_multiplicity_multiple_extension': lambda s: len(base_properties(s)) <= 1 or all(p.is_(0, 1) for p in base_properties(s)),
    'InformationFlow.convey_classifiers': lambda s: all(any(kind(s, c, name) for name in ('Class', 'Interface', 'InformationItem', 'Signal', 'Component')) for c in s.conveyed),
    'Constraint.boolean_value': lambda s: kind(s, s.specification, 'LiteralBoolean') or primitive(required(s.specification).type, 'Boolean'),
    'Constraint.no_side_effects': lambda s: expression_fact(required(s.specification), 'pure'),
    'MultiplicityElement.value_specification_no_side_effects': lambda s: all(expression_fact(v, 'pure') for v in (s.lowerValue, s.upperValue) if v is not None),
    'MultiplicityElement.value_specification_constant': lambda s: all(expression_fact(v, 'constant') for v in (s.lowerValue, s.upperValue) if v is not None),
})


@invariant('Profile.references_same_metamodel')
def same_reference_metamodel(self):
    # The published formula only checks nonemptiness, not the shared metamodel.
    def root_package(element):
        current, root, seen = element, None, set()
        while current is not None:
            if current in seen: raise ValueError('Cyclic metamodel ownership')
            seen.add(current)
            if kind(self, current, 'Package'): root = current
            current = current.owner
        return root
    references = [required(i.importedElement) for i in self.metaclassReference]
    for reference in self.metamodelReference:
        package = required(reference.importedPackage)
        references.append(package)
        references.extend(required(i.importedElement) for i in package.elementImport)
    if not references: return False
    roots = {root_package(reference) for reference in references}
    return None not in roots and len(roots) == 1


@invariant('Stereotype.name_not_clash')
def stereotype_keyword(self):
    # The standard keywords are metaclass names with an initial lower-case letter.
    extended = [p.type for p in base_properties(self) if kind(self, p.type, 'Class')]
    keywords = {c.name[:1].lower() + c.name[1:] for c in extended if c.name is not None}
    return self.name is None or self.name.casefold() not in {keyword.casefold() for keyword in keywords}


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
