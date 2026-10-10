import unittest
import Uml
from umltools.ocl import evaluate, OclUnsupported


class PackageTests(unittest.TestCase):
    def test_public_packages(self):
        from Uml.StateMachines import State
        self.assertIs(State, Uml.StateMachine.State)
        self.assertIs(Uml.Packages.Model, Uml.Model)
        self.assertEqual(len(Uml._classes.__all__), 255)


class OwnershipTests(unittest.TestCase):
    def test_ownership_names_and_transitive_query(self):
        model = Uml.Packages.Model(name='Shop')
        cls = Uml.StructuredClassifiers.Class(name='Customer')
        prop = Uml.Classification.Property(name='id')
        model.packagedElement.append(cls)
        cls.ownedAttribute.append(prop)
        self.assertIs(prop.owner, cls)
        self.assertIs(prop.class_, cls)
        self.assertIs(prop.namespace, cls)
        self.assertEqual(prop.qualifiedName, 'Shop::Customer::id')
        self.assertEqual(model.allOwnedElements(), [cls, prop])
        cls.ownedAttribute.remove(prop)
        self.assertIsNone(prop.owner)
        self.assertIsNone(prop.class_)

    def test_inverse_edit_and_collection_reference(self):
        cls = Uml.Class()
        prop = Uml.Property()
        view = cls.ownedAttribute
        prop.class_ = cls
        self.assertEqual(view, [prop])
        prop.class_ = None
        self.assertEqual(view, [])
        self.assertIsNone(prop.owner)

    def test_failed_bulk_edit_is_atomic(self):
        one, two = Uml.Model(), Uml.Model()
        cls, other = Uml.Class(), Uml.Class()
        one.packagedElement.append(cls)
        with self.assertRaises(ValueError):
            two.packagedElement.extend([other, cls])
        self.assertEqual(two.packagedElement, [])
        self.assertIsNone(other.owner)
        self.assertIs(cls.owner, one)
        with self.assertRaises(ValueError):
            one.packagedElement.append(one)
        self.assertEqual(one.packagedElement, [cls])

    def test_mutation_type_and_uniqueness(self):
        model, cls = Uml.Model(), Uml.Class()
        model.packagedElement.extend([cls, cls])
        self.assertEqual(model.packagedElement, [cls])
        with self.assertRaises(TypeError): model.packagedElement.append('wrong')
        with self.assertRaises(TypeError): model.packagedElement[0] = None
        self.assertEqual(model.packagedElement, [cls])

    def test_constructor_failure_rolls_back_external_links(self):
        prop = Uml.Property()
        with self.assertRaises(TypeError): Uml.Class(ownedAttribute=[prop], name=42)
        self.assertIsNone(prop.owner)
        self.assertIsNone(prop.class_)


class OclTests(unittest.TestCase):
    def setUp(self): self.element = Uml.Class(name='Customer')

    def test_arithmetic_condition_and_null(self):
        self.assertEqual(evaluate('if name <> null then 2 + 3 * 4 else 0 endif', self.element), 14)
        self.assertIsNone(evaluate('null implies false', self.element))
        self.assertTrue(evaluate('false implies invalid', self.element))
        self.assertEqual(evaluate("let x : String = 'A' in x.concat('B')", self.element), 'AB')

    def test_collection_iterators(self):
        self.assertTrue(evaluate('Sequence{1,2,3}->forAll(x | x > 0)', self.element))
        self.assertEqual(evaluate('Sequence{1,2,3}->select(x | x > 1)', self.element), [2,3])
        self.assertEqual(evaluate('Sequence{1,2,3}->iterate(x : Integer; total : Integer = 0 | total + x)', self.element), 6)
        self.assertTrue(evaluate('self.oclIsKindOf(Classifier)', self.element))
        self.assertEqual(evaluate('VisibilityKind::public', self.element), Uml.VisibilityKind.public)

    def test_specification_operations_and_derived_bounds(self):
        self.assertEqual(self.element.separator(), '::')
        self.assertTrue(self.element.mustBeOwned())
        prop = Uml.Property()
        self.assertEqual(prop.lower, 1)
        self.assertEqual(prop.upper, 1)
        self.assertFalse(prop.isMultivalued())

    def test_unsupported_syntax_is_explicit(self):
        with self.assertRaises(OclUnsupported): evaluate('self@pre', self.element)
        with self.assertRaises(OclUnsupported): evaluate("__import__('os')", self.element)
        with self.assertRaises(OclUnsupported): evaluate("self.__setattr__('name', 'changed')", self.element)
        self.assertEqual(self.element.name, 'Customer')

    def test_bag_and_set_multiplicity(self):
        self.assertEqual(evaluate('Bag{1,1}->union(Bag{1,2})->size()', self.element), 4)
        self.assertEqual(evaluate('Set{1,1}->union(Set{1,2})->size()', self.element), 2)
        self.assertIsNone(evaluate('Set{1}->forAll(x | null)', self.element))
        with self.assertRaises(ValueError): evaluate('Set{1}->forAll(x | 42)', self.element)

    def test_multiple_iterator_variables(self):
        self.assertTrue(evaluate('Set{1,2}->forAll(x, y | x = y or x <> y)', self.element))
        self.assertEqual(evaluate('let x : Set(Integer) = Set{1,2}, y : Integer = 3 in x->size() + y', self.element), 5)

    def test_all_instances_derivation(self):
        target = Uml.Class()
        dependency = Uml.Dependency(client=[self.element], supplier=[target])
        self.assertIn(dependency, self.element.clientDependency)
        dependency.client.clear()
        self.assertNotIn(dependency, self.element.clientDependency)

    def test_recursive_validation_finds_child_failures(self):
        model = Uml.Model(packagedElement=[self.element])
        self.element.generalization.append(Uml.Generalization())
        shallow = model.validate()
        recursive = model.validate(recursive=True)
        self.assertNotIn(('multiplicity', 'Generalization-general'), shallow)
        self.assertIn(('multiplicity', 'Generalization-general'), recursive)
