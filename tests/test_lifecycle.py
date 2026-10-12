"""Logical deletion must work while ordinary Python references remain alive."""
import unittest
from unittest.mock import patch
import Uml
from umltools import ModelSession, DeletedElementError, DeletionRestrictedError
from umltools.native import instances, check
from umltools.stereotypes import apply_stereotype, applications
from umltools.interaction_mapping import bind_gate_endpoint
from semantic_cases import verifies


class DeletionCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    @verifies('Element-ownedElement', 'Element-owner', 'Classifier.attribute', 'NamedElement.clientDependency')
    def test_subtree_removal_clears_external_references_and_extents(self):
        prop = Uml.Property(name='x')
        cls = Uml.Class(ownedAttribute=[prop])
        other = Uml.Class()
        model = Uml.Model(packagedElement=[cls, other])
        dependency = Uml.Dependency(client=[cls], supplier=[other])
        user = Uml.Property(type=cls)
        cache = model.packagedElement
        doomed = set(cls.delete())
        self.assertEqual(doomed, {cls, prop})
        self.assertEqual(list(cache), [other])
        self.assertIsNone(user.type)
        self.assertEqual(list(dependency.client), [])
        self.assertNotIn(cls, instances(other, 'Class'))
        self.assertNotIn(cls, self.session.elements)
        self.assertNotIn(cls, cls.__instances__)
        self.assertTrue(prop.is_deleted)
        self.assertEqual(cls.delete(), ())
        self.assertEqual(model.allOwnedElements(), [other])

    def test_required_references_become_explicit_validation_failures(self):
        base, child = Uml.Class(), Uml.Class()
        relation = Uml.Generalization(general=base, specific=child)
        base.delete()
        self.assertIsNone(relation.general)
        self.assertIn(('multiplicity', 'Generalization-general'), relation.validate())

    def test_session_retains_unowned_live_elements_until_explicit_deletion(self):
        import gc
        import weakref
        anchor, temporary = Uml.Class(), Uml.Class()
        reference = weakref.ref(temporary)
        del temporary
        gc.collect()
        self.assertIsNotNone(reference())
        self.assertIn(reference(), instances(anchor, 'Class'))
        reference().delete()
        self.assertNotIn(reference(), instances(anchor, 'Class'))

    def test_restrict_refuses_external_references_atomically(self):
        cls = Uml.Class(ownedAttribute=[Uml.Property()])
        model = Uml.Model(packagedElement=[cls])
        referrer = Uml.Property(type=cls)
        with self.assertRaises(DeletionRestrictedError): cls.delete(on_references='restrict')
        self.assertFalse(cls.is_deleted)
        self.assertIs(referrer.type, cls)
        self.assertIs(cls.owner, model)
        self.assertEqual(len(cls.ownedAttribute), 1)
        referrer.type = None
        cls.delete(on_references='restrict')
        self.assertEqual(list(model.packagedElement), [])

    def test_no_cascade_refuses_children_and_deletes_a_leaf(self):
        cls, prop = Uml.Class(), Uml.Property()
        cls.ownedAttribute.append(prop)
        with self.assertRaises(DeletionRestrictedError): cls.delete(cascade=False)
        self.assertIs(prop.owner, cls)
        self.assertEqual(prop.delete(cascade=False), (prop,))
        self.assertEqual(list(cls.ownedAttribute), [])

    def test_tombstones_reject_reads_mutation_queries_validation_and_reuse(self):
        cls = Uml.Class(ownedAttribute=[Uml.Property()])
        cache = cls.ownedAttribute
        cls.delete()
        for action in (lambda: cls.name, lambda: setattr(cls, 'name', 'new'), lambda: cls.allParents(),
                       lambda: cls.validate(), lambda: check(cls, 'Classifier.no_cycles_in_generalization'),
                       lambda: len(cache), lambda: cache.append(Uml.Property()),
                       lambda: Uml.Property(type=cls), lambda: Uml.Class().conformsTo(cls)):
            with self.assertRaises(DeletedElementError): action()

    def test_references_from_other_sessions_are_cleaned_without_deleting_their_elements(self):
        cls = Uml.Class()
        with ModelSession() as other:
            prop = Uml.Property(type=cls)
        cls.delete()
        self.assertIsNone(prop.type)
        self.assertFalse(prop.is_deleted)
        self.assertIn(prop, other.elements)

    def test_failure_restores_collection_identity_ownership_and_all_references(self):
        cls = Uml.Class(ownedAttribute=[Uml.Property()])
        model = Uml.Model(packagedElement=[cls])
        referrer = Uml.Property(type=cls)
        cache = model.packagedElement
        original = referrer._assign
        def fail(name, value):
            if name == 'type' and value is None: raise ValueError('Injected mutation failure')
            return original(name, value)
        with patch.object(referrer, '_assign', fail):
            with self.assertRaises(ValueError): cls.delete()
        self.assertIs(model.packagedElement, cache)
        self.assertEqual(list(cache), [cls])
        self.assertIs(cls.owner, model)
        self.assertIs(referrer.type, cls)
        self.assertFalse(cls.is_deleted)
        self.assertEqual(len(cls.ownedAttribute), 1)

    def test_semantic_adapter_mappings_are_cleaned(self):
        gate, endpoint = Uml.Gate(), Uml.Class()
        message = Uml.Message(sendEvent=gate)
        bind_gate_endpoint(message, gate, endpoint)
        endpoint.delete()
        self.assertEqual(message._gate_endpoint_bindings, {})
        with self.assertRaises(DeletedElementError): bind_gate_endpoint(message, gate, endpoint)

    def test_shared_composite_subsets_are_deleted_once_and_inverse_ends_are_removed(self):
        node = Uml.StructuredActivityNode()
        activity = Uml.Activity(structuredNode=[node])
        self.assertEqual(set(activity.delete()), {activity, node})
        a, b = Uml.Property(), Uml.Property()
        association = Uml.Association(ownedEnd=[a, b])
        a.delete()
        self.assertEqual(list(association.memberEnd), [b])
        self.assertEqual(list(association.ownedEnd), [b])
        self.assertIs(b.association, association)

    def stereotype_fixture(self):
        profile, metaclass = Uml.Profile(name='Domain'), Uml.Class(name='Class')
        stereotype = Uml.Stereotype(name='Tagged')
        prop = Uml.Property(name='base_Class', type=metaclass)
        end = Uml.ExtensionEnd(type=stereotype, aggregation=Uml.AggregationKind.composite)
        extension = Uml.Extension(ownedEnd=end, memberEnd=[prop, end])
        stereotype.ownedAttribute.append(prop)
        profile.packagedElement.extend([stereotype, extension])
        element = Uml.Class()
        model = Uml.Model(packagedElement=[element], profileApplication=[Uml.ProfileApplication(appliedProfile=profile)])
        return profile, stereotype, prop, element, model

    def test_deleted_base_detaches_runtime_and_removes_modeled_applications(self):
        profile, stereotype, prop, element, model = self.stereotype_fixture()
        app = apply_stereotype(element, stereotype)
        element.delete()
        self.assertIsNone(app.element)
        self.assertEqual(applications(element), ())
        with self.assertRaises(DeletedElementError): app.rebind(element)
        other = Uml.InstanceSpecification(classifier=[prop.type])
        model.packagedElement.append(other)
        value = Uml.InstanceValue(instance=other)
        modeled = Uml.InstanceSpecification(classifier=[stereotype], slot=[Uml.Slot(definingFeature=prop, value=[value])])
        model.packagedElement.append(modeled)
        other.delete()
        self.assertTrue(modeled.is_deleted)
        self.assertTrue(value.is_deleted)

    def test_deleted_profile_detaches_applications_and_removes_profile_application(self):
        profile, stereotype, prop, element, model = self.stereotype_fixture()
        app = apply_stereotype(element, stereotype)
        application = model.profileApplication[0]
        profile.delete()
        self.assertTrue(application.is_deleted)
        self.assertEqual(list(model.profileApplication), [])
        self.assertIsNone(app.element)
        self.assertFalse(element.is_deleted)

    def test_invalid_options_never_change_the_model(self):
        cls = Uml.Class()
        with self.assertRaises(ValueError): cls.delete(on_references='unknown')
        with self.assertRaises(TypeError): cls.delete(cascade=1)
        self.assertFalse(cls.is_deleted)

    def test_deleted_references_invalidate_analyzer_facts(self):
        from umltools.expression_semantics import register_expression_facts, expression_fact, register_collection_type, is_collection_type
        from umltools.native import NativeNotImplemented
        expression, reference = Uml.OpaqueExpression(), Uml.Variable()
        register_expression_facts(expression, references=[reference], pure=True)
        reference.delete()
        with self.assertRaises(NativeNotImplemented): expression_fact(expression, 'references')
        collection = Uml.Class()
        register_collection_type(collection)
        collection.delete()
        self.assertFalse(is_collection_type(collection))
        with self.assertRaises(DeletedElementError): register_collection_type(collection)

    def test_restrict_protects_runtime_applications_of_a_deleted_stereotype(self):
        profile, stereotype, prop, element, model = self.stereotype_fixture()
        app = apply_stereotype(element, stereotype)
        with self.assertRaises(DeletionRestrictedError): profile.delete(on_references='restrict')
        self.assertFalse(stereotype.is_deleted)
        self.assertIs(app.element, element)
        profile.delete()
        self.assertIsNone(app.element)

    def test_application_cleanup_failure_restores_the_graph_and_application(self):
        profile, stereotype, prop, element, model = self.stereotype_fixture()
        app = apply_stereotype(element, stereotype)
        original = app.detach
        def fail():
            original()
            raise ValueError('Injected application cleanup failure')
        with patch.object(app, 'detach', fail):
            with self.assertRaises(ValueError): element.delete()
        self.assertFalse(element.is_deleted)
        self.assertIs(element.owner, model)
        self.assertIs(app.element, element)
        self.assertEqual(applications(element), (app,))

    def test_deletion_can_repair_a_model_with_cyclic_stereotype_generalizations(self):
        first, second = Uml.Stereotype(), Uml.Stereotype()
        first.generalization.append(Uml.Generalization(general=second))
        second.generalization.append(Uml.Generalization(general=first))
        modeled = Uml.InstanceSpecification(classifier=[first])
        unrelated = Uml.Class()
        unrelated.delete()  # An invalid stereotype elsewhere must not block deletion.
        first.delete()
        self.assertTrue(first.is_deleted)
        self.assertTrue(modeled.is_deleted)
        self.assertFalse(second.is_deleted)
        self.assertIsNone(second.generalization[0].general)
