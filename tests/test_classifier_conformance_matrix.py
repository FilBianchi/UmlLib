"""Explicit boundary oracles, independent of native rule implementations.

Source anchors and version decisions are described in CONFORMANCE_MATRIX.md.
These are behavioral examples, not a claim of exhaustive UML conformance.
"""
import importlib
import itertools
import unittest

from umltools.xmi import XmiDocument, loads
from semantic_cases import verifies


VERSIONS = ('2.4.1', '2.5.1')


def facade(version):
    return importlib.import_module('Uml241' if version == '2.4.1' else 'Uml251')


def bounded(u, cls, low, high, **values):
    return cls(lowerValue=u.LiteralInteger(value=low),
               upperValue=u.LiteralUnlimitedNatural(value=high), **values)


def invariant(version, element, rule):
    if version == '2.4.1':
        return facade(version)._engine.native.check(element, rule)
    from umltools.native import check
    return check(element, rule)


class ClassifierMatrix(unittest.TestCase):
    @verifies('Property.subsetting_rules', 'Property.subsetting_context_conforms', 'Property.subsetted_property_names')
    def test_subsetting_type_upper_bound_name_and_context_grid(self):
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new(semantic_version=version)
            with doc.session:
                base, child, type_, subtype, unrelated = [u.Class() for _ in range(5)]
                child.generalization.append(u.Generalization(general=base))
                subtype.generalization.append(u.Generalization(general=type_))
                broad = bounded(u, u.Property, 1, 4, name='all', type=type_)
                narrow = bounded(u, u.Property, 0, 1, name='some', type=type_, subsettedProperty=[broad])
                base.ownedAttribute.append(broad)
                child.ownedAttribute.append(narrow)
                for low, high, typed in itertools.product((0, 1), (1, 4, 5, float('inf')), ('same', 'subtype', 'unrelated')):
                    with self.subTest(version=version, low=low, high=high, type=typed):
                        narrow.lowerValue.value, narrow.upperValue.value = low, high
                        narrow.type = {'same': type_, 'subtype': subtype, 'unrelated': unrelated}[typed]
                        # Subsetting restricts upper, not lower (unlike redefinition).
                        self.assertEqual(invariant(version, narrow, 'Property.subsetting_rules'),
                                         high <= 4 and typed != 'unrelated')
                self.assertTrue(invariant(version, narrow, 'Property.subsetting_context_conforms'))
                child.generalization.clear()
                self.assertFalse(invariant(version, narrow, 'Property.subsetting_context_conforms'))
                child.generalization.append(u.Generalization(general=base))
                self.assertTrue(invariant(version, narrow, 'Property.subsetting_context_conforms'))
                narrow.name = 'all'
                self.assertFalse(invariant(version, narrow, 'Property.subsetted_property_names'))
                narrow.name = 'some'
                self.assertTrue(invariant(version, narrow, 'Property.subsetted_property_names'))

    @verifies('Connector.types', 'Connector.roles')
    def test_connector_type_conformance_arity_missing_role_and_repair(self):
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new(semantic_version=version)
            with doc.session:
                owner, type_, subtype, unrelated = [u.Class() for _ in range(4)]
                subtype.generalization.append(u.Generalization(general=type_))
                a, b = u.Property(type=type_), u.Property(type=type_)
                owner.ownedAttribute.extend([a, b])
                association = u.Association(ownedEnd=[u.Property(type=type_), u.Property(type=type_)])
                ea, eb = u.ConnectorEnd(role=a), u.ConnectorEnd(role=b)
                connector = u.Connector(type=association, end=[ea, eb])
                owner.ownedConnector.append(connector)
                for left, right in itertools.product(('same', 'subtype', 'unrelated'), repeat=2):
                    with self.subTest(version=version, left=left, right=right):
                        types = {'same': type_, 'subtype': subtype, 'unrelated': unrelated}
                        a.type, b.type = types[left], types[right]
                        self.assertEqual(invariant(version, connector, 'Connector.types'),
                                         left != 'unrelated' and right != 'unrelated')
                a.type = b.type = type_
                connector.end.remove(eb)
                self.assertFalse(invariant(version, connector, 'Connector.types'))
                connector.end.append(eb)
                ea.role = None
                with self.assertRaises(ValueError):
                    invariant(version, connector, 'Connector.types')
                ea.role = a
                self.assertTrue(invariant(version, connector, 'Connector.types'))
                self.assertTrue(invariant(version, connector, 'Connector.roles'))
                owner.ownedAttribute.remove(a)
                self.assertFalse(invariant(version, connector, 'Connector.roles'))
                owner.ownedAttribute.append(a)
                self.assertTrue(invariant(version, connector, 'Connector.roles'))

    @verifies('Generalization-general', 'Classifier.non_final_parents')
    def test_missing_general_diagnostics_are_repaired_without_false_success(self):
        for version in VERSIONS:
            doc = XmiDocument.new(semantic_version=version)
            child = doc.create('Class', owner=doc.roots[0], feature='packagedElement', name='Child')
            parent = doc.create('Class', owner=doc.roots[0], feature='packagedElement', name='Parent')
            generalization = doc.create('Generalization', owner=child, feature='generalization')
            report = doc.validation_report()
            self.assertTrue(any(i.element is generalization and i.rule == 'Generalization-general'
                                and i.status == 'violation' for i in report.issues))
            self.assertTrue(any(i.element is child and i.status == 'evaluation_error' for i in report.issues))
            doc.set_value(generalization, 'general', parent)
            repaired = doc.validation_report()
            self.assertFalse(any(i.rule == 'Generalization-general' or
                                 (i.element is child and i.status == 'evaluation_error') for i in repaired.issues))
            # Only assert this repaired contract, not global UML conformance.

    @verifies('StructuredClassifier-ownedAttribute', 'Property-class')
    def test_move_failure_transfer_detach_reattach_has_independent_expected_owners(self):
        for version in VERSIONS:
            doc = XmiDocument.new(semantic_version=version)
            model = doc.roots[0]
            a = doc.create('Class', owner=model, feature='packagedElement', name='A')
            b = doc.create('Class', owner=model, feature='packagedElement', name='B')
            nested = doc.create('Class', owner=a, feature='nestedClassifier', name='Nested')
            p = doc.create('Port', owner=a, feature='ownedAttribute', name='p')
            cached_a, cached_b = a.ownedAttribute, b.ownedAttribute
            identity = doc.identity(p)
            doc.move(p, owner=b, feature='ownedAttribute')
            self.assertEqual(list(cached_a), [])
            self.assertEqual(list(cached_b), [p])
            self.assertIs(p.class_, b)
            before = doc.dumps()
            with self.assertRaises(ValueError):
                doc.move(a, owner=nested, feature='nestedClassifier')
            self.assertEqual(doc.dumps(), before)
            self.assertIs(a.owner, model)
            self.assertIs(nested.owner, a)
            doc.detach(p)
            self.assertEqual(list(cached_b), [])
            self.assertIsNone(p.class_)
            doc.move(p, owner=a, feature='ownedAttribute')
            self.assertEqual(list(cached_a), [p])
            self.assertIs(p.class_, a)
            self.assertIs(doc.resolve(identity), p)

    @verifies('Property.isConsistentWith')
    def test_redefinition_bounds_type_and_composition_grid(self):
        # 180 independently specified combinations per semantic version.
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new(semantic_version=version)
            with doc.session:
                base, child, type_, subtype, unrelated = [u.Class() for _ in range(5)]
                child.generalization.append(u.Generalization(general=base))
                subtype.generalization.append(u.Generalization(general=type_))
                old = bounded(u, u.Property, 1, 4, type=type_)
                new = bounded(u, u.Property, 1, 4, type=type_)
                base.ownedAttribute.append(old)
                child.ownedAttribute.append(new)
                for low, high, typed, composite_old, composite_new in itertools.product(
                        (0, 1, 2, 4), (2, 4, 5, float('inf')),
                        ('same', 'subtype', 'unrelated'), (False, True), (False, True)):
                    if low > high:
                        continue  # malformed multiplicities are a separate contract
                    with self.subTest(version=version, low=low, high=high, type=typed,
                                      old_composite=composite_old, new_composite=composite_new):
                        new.lowerValue.value, new.upperValue.value = low, high
                        new.type = {'same': type_, 'subtype': subtype, 'unrelated': unrelated}[typed]
                        old.aggregation = u.AggregationKind.composite if composite_old else u.AggregationKind.none
                        new.aggregation = u.AggregationKind.composite if composite_new else u.AggregationKind.none
                        expected = (low >= 1 and high <= 4 and typed != 'unrelated'
                                    and (not composite_old or composite_new))
                        self.assertEqual(old.isConsistentWith(new), expected)

    @verifies('Property.isCompatibleWith')
    def test_property_metaclass_direction_is_version_specific(self):
        # The 2.4.1 OCL reverses the metaclass test relative to its prose.
        # Preserve the declared version contract rather than guessing an erratum.
        expected = {'2.4.1': (True, False), '2.5.1': (False, True)}
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new(semantic_version=version)
            with doc.session:
                type_ = u.Class()
                property_, port = u.Property(type=type_), u.Port(type=type_)
                self.assertEqual((property_.isCompatibleWith(port), port.isCompatibleWith(property_)),
                                 expected[version])

    @verifies('Property.opposite', 'Property.isNavigable')
    def test_association_ownership_and_navigation_grid(self):
        for version, owned_left, owned_right, navigable in itertools.product(VERSIONS, (False, True), (False, True), (False, True)):
            with self.subTest(version=version, owned_left=owned_left, owned_right=owned_right, navigable=navigable):
                u = facade(version)
                doc = XmiDocument.new(semantic_version=version)
                with doc.session:
                    left, right = u.Class(), u.Class()
                    a, b = u.Property(type=right), u.Property(type=left)
                    association = u.Association(memberEnd=[a, b])
                    for end, cls, owned in ((a, left, owned_left), (b, right, owned_right)):
                        (association.ownedEnd if owned else cls.ownedAttribute).append(end)
                        if owned and navigable:
                            association.navigableOwnedEnd.append(end)
                    has_opposite = version == '2.5.1' or not (owned_left or owned_right)
                    self.assertIs(a.opposite, b if has_opposite else None)
                    self.assertIs(b.opposite, a if has_opposite else None)
                    self.assertEqual(a.isNavigable(), not owned_left or navigable)
                    self.assertEqual(b.isNavigable(), not owned_right or navigable)
                    association.ownedEnd.append(u.Property(type=left))
                    self.assertIsNone(a.opposite)
                    self.assertIsNone(b.opposite)

    @verifies('Classifier.allParents', 'Classifier.inheritedMember', 'Classifier.no_cycles_in_generalization')
    def test_diamond_inheritance_mutate_remove_and_repair(self):
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new(semantic_version=version)
            with doc.session:
                root, left, right, leaf = [u.Class(name=n) for n in ('Root', 'Left', 'Right', 'Leaf')]
                shared = u.Property(name='shared', visibility=u.VisibilityKind.public)
                hidden = u.Property(name='hidden', visibility=u.VisibilityKind.private)
                root.ownedAttribute.extend([shared, hidden])
                left.generalization.append(u.Generalization(general=root))
                right.generalization.append(u.Generalization(general=root))
                first, second = u.Generalization(general=left), u.Generalization(general=right)
                leaf.generalization.extend([first, second])
                self.assertEqual(set(leaf.allParents()), {root, left, right})
                self.assertEqual(list(leaf.inheritedMember).count(shared), 1)
                self.assertNotIn(hidden, leaf.inheritedMember)
                leaf.generalization.remove(first)
                self.assertEqual(set(leaf.allParents()), {root, right})
                leaf.generalization.remove(second)
                self.assertEqual(list(leaf.inheritedMember), [])
                leaf.generalization.append(first)
                self.assertIn(shared, leaf.inheritedMember)
                first.general = None
                with self.assertRaises(ValueError):
                    leaf.allParents()
                first.general = right
                self.assertEqual(set(leaf.allParents()), {root, right})

    @verifies('ConnectorEnd.definingEnd', 'Port.provided', 'Port.required', 'ConnectableElement.end')
    def test_connector_order_conjugation_delete_and_xmi_identity(self):
        for version in VERSIONS:
            u = facade(version)
            doc = XmiDocument.new('Matrix', semantic_version=version)
            model = doc.roots[0]
            with doc.session:
                interface = u.Interface(name='Service')
                owner = u.Class(name='Owner')
                a, b = u.Port(name='a', type=interface), u.Port(name='b', type=interface)
                owner.ownedAttribute.extend([a, b])
                x, y = u.Property(name='x', type=interface), u.Property(name='y', type=interface)
                association = u.Association(name='Wire', ownedEnd=[x, y])
                ea, eb = u.ConnectorEnd(role=a), u.ConnectorEnd(role=b)
                connector = u.Connector(name='wire', type=association, end=[ea, eb])
                owner.ownedConnector.append(connector)
                model.packagedElement.extend([interface, owner, association])
                self.assertIs(ea.definingEnd, x)
                connector.end.reverse()
                self.assertIs(ea.definingEnd, y)
                a.isConjugated = True
                self.assertEqual(list(a.provided), [])
                self.assertEqual(list(a.required), [interface])
            restored = loads(doc.dumps(), semantic_version='auto')
            by_name = {e.name: e for e in restored.session.elements if getattr(e, 'name', None)}
            saved = by_name['wire']
            self.assertIs(saved.type, by_name['Wire'])
            self.assertIs(saved.end[0].role, by_name['b'])
            self.assertIs(saved.end[1].role, by_name['a'])
            self.assertIs(saved.end[1].definingEnd, by_name['y'])
            self.assertIs(by_name['a'].owner, by_name['Owner'])
            restored.delete(saved.end[1])
            self.assertEqual(list(by_name['a'].end), [])
            self.assertEqual(len(saved.end), 1)


if __name__ == '__main__':
    unittest.main()
