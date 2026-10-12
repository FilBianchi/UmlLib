"""Declaration sweeps and independent mutation/lifecycle contract families."""
import unittest
import Uml
from umltools import SPECIFICATIONS, ModelSession, DeletedElementError, UnsupportedSemanticsError
from semantic_cases import verifies


def concrete(owner, property_id=None):
    registry = Uml.Class.__registry__
    choices = [cls for cls in registry.values() if isinstance(cls, type) and hasattr(cls, '__spec__')
               and not cls.__spec__.abstract and issubclass(cls, registry[owner])
               and (property_id is None or any(p.id == property_id for p in cls.properties().values()))]
    if not choices: return None
    return min(choices, key=lambda c: (len(c.__mro__), c.__spec__.name))


class StructuralContractCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    def test_all_effective_stored_declarations_defaults_and_wrong_types(self):
        checked, inaccessible = set(), set()
        for spec in SPECIFICATIONS.values():
            for prop in spec.properties.values():
                if prop.flags.get('isDerived') == 'true': continue
                cls = concrete(spec.name, prop.id)
                if cls is None:
                    inaccessible.add(prop.id)
                    continue
                with self.subTest(property=prop.id):
                    obj = cls()
                    value = getattr(obj, prop.name)
                    many = prop.upper is None or prop.upper > 1
                    if many:
                        self.assertEqual(list(value), [])
                        self.assertIs(getattr(obj, prop.name), value)
                    elif prop.default is None: self.assertIsNone(value)
                    else:
                        from umltools.contracts import validate_item
                        validate_item(obj, value, prop.type)
                    with self.assertRaises(TypeError): setattr(obj, prop.name, [object()] if many else object())
                    self.assertIs(getattr(obj, prop.name), value)
                    checked.add(prop.id)
        self.assertEqual(len(checked) + len(inaccessible), 549)
        # Declarations hidden by redefinitions are inventory obligations, not silently counted as executed setters.
        self.assertEqual(inaccessible, set())

    def test_all_stored_setters_accept_values_of_the_declared_type(self):
        primitive = {'Boolean': True, 'Integer': 1, 'Real': 1.5, 'UnlimitedNatural': 2, 'String': 'audit'}
        registry = Uml.Class.__registry__
        tested = set()
        for spec in SPECIFICATIONS.values():
            for prop in spec.properties.values():
                if prop.flags.get('isDerived') == 'true': continue
                with self.subTest(property=prop.id):
                    obj = concrete(spec.name, prop.id)()
                    if prop.type in primitive: value = primitive[prop.type]
                    elif hasattr(registry[prop.type], '__spec__'): value = concrete(prop.type)()
                    else: value = next(iter(registry[prop.type]))
                    many = prop.upper is None or prop.upper > 1
                    setattr(obj, prop.name, [value] if many else value)
                    actual = getattr(obj, prop.name)
                    self.assertEqual(list(actual), [value]) if many else self.assertEqual(actual, value)
                    tested.add(prop.id)
        self.assertEqual(len(tested), 549)

    @verifies('DurationObservation-event', 'DurationObservation-firstEvent', 'OpaqueBehavior-body', 'OpaqueBehavior-language')
    def test_unique_bounds_order_bags_and_atomic_collection_operations(self):
        a, b, c = Uml.Class(), Uml.Class(), Uml.Class()
        observation = Uml.DurationObservation(event=[a, a, b], firstEvent=[True, True, False])
        self.assertEqual(list(observation.event), [a, b])
        self.assertEqual(list(observation.firstEvent), [True, False])
        cached = observation.event
        cached.append(a)
        self.assertEqual(list(cached), [a, b])
        with self.assertRaises(ValueError): cached.extend([a, c])
        self.assertIs(observation.event, cached)
        self.assertEqual(list(cached), [a, b])
        cached.reverse()
        self.assertEqual(list(cached), [b, a])
        with self.assertRaises(TypeError): cached[0:1] = [Uml.Class(), None]
        self.assertEqual(list(cached), [b, a])
        body = Uml.OpaqueBehavior(body=['x', 'x'], language=['Python', 'Python'])
        self.assertEqual(list(body.body), ['x', 'x'])
        self.assertEqual(list(body.language), ['Python'])

    @verifies('Transition-source', 'Vertex-outgoing', 'Transition-target', 'Vertex-incoming')
    def test_noncomposite_inverse_reassignment_and_clear_from_both_ends(self):
        first, second, target = Uml.State(), Uml.State(), Uml.State()
        transition = Uml.Transition(source=first, target=target)
        self.assertEqual(list(first.outgoing), [transition])
        with self.assertRaises(UnsupportedSemanticsError): second.outgoing = [transition]
        transition.source = second
        self.assertIs(transition.source, second)
        self.assertEqual(list(first.outgoing), [])
        self.assertEqual(list(second.outgoing), [transition])
        transition.target = None
        self.assertIsNone(transition.target)
        transition.source = None
        self.assertEqual(list(second.outgoing), [])

    @verifies('Generalization-generalizationSet', 'GeneralizationSet-generalization')
    def test_stored_many_to_many_inverses_and_transactional_invalid_edit(self):
        relation = Uml.Generalization()
        first, second = Uml.GeneralizationSet(), Uml.GeneralizationSet()
        first.generalization.append(relation)
        self.assertEqual(list(relation.generalizationSet), [first])
        relation.generalizationSet.append(second)
        self.assertEqual(list(second.generalization), [relation])
        cached = relation.generalizationSet
        with self.assertRaises(TypeError): cached[:] = [second, 'invalid']
        self.assertEqual(list(cached), [first, second])
        self.assertEqual(list(first.generalization), [relation])
        relation.generalizationSet = [second]
        self.assertEqual(list(first.generalization), [])
        second.generalization.clear()
        self.assertEqual(list(cached), [])

    @verifies('Class-ownedAttribute', 'Property-class', 'Element-owner', 'Element-ownedElement')
    def test_composite_reparenting_aliases_cycle_and_constructor_rollback(self):
        a, b, prop = Uml.Class(), Uml.Class(), Uml.Property()
        a.ownedAttribute.append(prop)
        self.assertIs(prop.class_, a)
        self.assertIs(prop.owner, a)
        before = set(self.session.elements)
        with self.assertRaises(ValueError): Uml.Class(ownedAttribute=[prop])
        self.assertEqual(self.session.elements, before)
        self.assertEqual(list(a.ownedAttribute), [prop])
        prop.class_ = b
        self.assertEqual(list(a.ownedAttribute), [])
        self.assertEqual(list(b.ownedAttribute), [prop])
        self.assertIs(prop.owner, b)
        b.nestedClassifier.append(a)
        with self.assertRaises(ValueError): a.nestedClassifier.append(b)
        self.assertIs(a.owner, b)
        self.assertIsNone(b.owner)

    @verifies('Activity-structuredNode', 'Activity-node', 'Activity-group', 'StructuredActivityNode-activity')
    def test_multiple_subset_witnesses_superset_removal_and_failure_rollback(self):
        first, other = Uml.Activity(), Uml.Activity()
        node = Uml.StructuredActivityNode()
        first.structuredNode.append(node)
        nodes, groups = first.node, first.group
        self.assertIn(node, nodes)
        self.assertIn(node, groups)
        with self.assertRaises(ValueError): other.structuredNode.append(node)
        self.assertEqual(list(other.node), [])
        self.assertEqual(list(other.group), [])
        self.assertIs(node.activity, first)
        nodes.remove(node)
        self.assertEqual(list(first.structuredNode), [])
        self.assertIn(node, groups)
        self.assertIs(node.owner, first)
        groups.remove(node)
        self.assertIsNone(node.owner)
        node.activity = first
        self.assertEqual(list(first.structuredNode), [node])
        node.activity = other
        self.assertEqual(list(first.structuredNode), [])
        self.assertEqual(list(first.node), [])
        self.assertEqual(list(first.group), [])
        self.assertEqual(list(other.structuredNode), [node])
        self.assertIs(node.owner, other)
        self.assertIs(node.inActivity, other)
        node.inActivity = first
        self.assertIs(node.activity, first)
        self.assertIs(node.owner, first)
        self.assertEqual(list(other.structuredNode), [])
        node.activity = None
        self.assertIsNone(node.inActivity)
        self.assertIsNone(node.owner)
        self.assertEqual(list(first.group), [])
        self.assertEqual(list(first.node), [])

    @verifies('Operation-ownedParameter', 'BehavioralFeature-ownedParameter', 'Parameter-operation', 'Classifier-attribute')
    def test_redefinition_stored_superset_and_derived_union_write_protection(self):
        p, operation = Uml.Parameter(), Uml.Operation()
        operation.ownedParameter.append(p)
        self.assertIs(p.operation, operation)
        self.assertEqual(list(operation.inputParameters()), [p])
        operation.ownedParameter.clear()
        self.assertIsNone(p.operation)
        classifier = Uml.Class(ownedAttribute=[Uml.Property()])
        derived = classifier.attribute
        derived.clear()
        self.assertEqual(len(classifier.attribute), 1)
        with self.assertRaises(UnsupportedSemanticsError): classifier.attribute = []

    @verifies('Dependency-client', 'NamedElement-clientDependency', 'Class-ownedAttribute', 'TypedElement-type')
    def test_cross_session_reference_diagnostics_inverse_links_and_deletion(self):
        foreign = Uml.Class()
        with ModelSession() as local:
            dependency = Uml.Dependency(client=[foreign])
            owner = Uml.Class(ownedAttribute=[Uml.Property(type=foreign)])
        self.assertIn(('cross session reference', 'Dependency-client'), dependency.validate())
        self.assertIn(('cross session reference', 'TypedElement-type'), owner.ownedAttribute[0].validate())
        # allInstances-based non-navigable queries only inspect the object's own extent.
        self.assertNotIn(dependency, foreign.clientDependency)
        foreign.delete()
        self.assertEqual(list(dependency.client), [])
        self.assertIsNone(owner.ownedAttribute[0].type)
        self.assertNotIn(('cross session reference', 'Dependency-client'), dependency.validate())
        self.assertIn(owner, local.elements)

    def test_cached_collection_reads_and_writes_reject_tombstone_owner(self):
        classifier = Uml.Class()
        cache = classifier.ownedAttribute
        classifier.delete()
        for access in (lambda: repr(cache), lambda: cache == [], lambda: len(cache),
                       lambda: cache.append(Uml.Property()), lambda: cache[:]):
            with self.assertRaises(DeletedElementError): access()

    def test_inventory_resolves_every_property_type_relation_and_evidence_link(self):
        from structural_audit import audit
        result = audit()
        self.assertEqual(result['counts'], {'structural property': 549, 'derived property': 73, 'association-owned property': 328})
        self.assertEqual(result['declaration_diagnostics'], [])
        self.assertEqual(sum(bool(p['declaration_sweeps']) for p in result['properties']), 549)
        for record in result['properties']:
            for example in record['declaration_sweeps'] + record['definition_examples'] + record['family_examples']:
                module, cls, test = example.split('.')
                self.assertTrue(callable(getattr(getattr(__import__(module), cls), test)))
