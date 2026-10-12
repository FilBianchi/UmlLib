"""Result contracts are tested independently of individual query algorithms."""
import unittest
from unittest.mock import patch
import Uml
from umltools import ModelSession, OperationResultError, SPECIFICATIONS
from umltools.native import OPERATIONS
from umltools.semantics import operation
from semantic_cases import verifies


class ContractCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    def result(self, obj, owner, name, value, *args):
        with patch.dict(OPERATIONS, {f'{owner}.{name}': lambda self, **kwargs: value}):
            return operation(obj, owner, name, args)

    def test_boolean_query_rejects_integer_and_missing_result(self):
        for value in (1, 'true', None, []):
            with self.subTest(value=value):
                with self.assertRaises(OperationResultError) as caught:
                    self.result(Uml.Class(), 'Element', 'mustBeOwned', value)
                self.assertEqual(caught.exception.operation, 'Element.mustBeOwned')
        self.assertIs(self.result(Uml.Class(), 'Element', 'mustBeOwned', False), False)

    def test_optional_scalar_does_not_accept_a_collection(self):
        literal = Uml.LiteralInteger()
        self.assertIsNone(self.result(literal, 'ValueSpecification', 'integerValue', None))
        with self.assertRaises(OperationResultError): self.result(literal, 'ValueSpecification', 'integerValue', [1])
        with self.assertRaises(OperationResultError): self.result(literal, 'ValueSpecification', 'integerValue', True)

    def test_collection_result_checks_shape_item_type_and_uniqueness(self):
        model, child = Uml.Model(), Uml.Class()
        for value in (None, child, [None], ['not an Element'], [child, child]):
            with self.subTest(value=value):
                with self.assertRaises(OperationResultError): self.result(model, 'Element', 'allOwnedElements', value)
        self.assertEqual(self.result(model, 'Element', 'allOwnedElements', [child]), [child])
        self.assertEqual(self.result(model, 'Element', 'allOwnedElements', {child}), {child})

    def test_ordered_collection_does_not_accept_an_unordered_set(self):
        obj, namespace = Uml.Class(), Uml.Package()
        with self.assertRaises(OperationResultError): self.result(obj, 'NamedElement', 'allNamespaces', {namespace})
        self.assertEqual(self.result(obj, 'NamedElement', 'allNamespaces', (namespace,)), (namespace,))

    def test_enum_result_requires_the_declared_enumeration(self):
        message = Uml.Message()
        self.assertEqual(self.result(message, 'Message', 'messageKind', Uml.MessageKind.unknown), Uml.MessageKind.unknown)
        for value in ('unknown', Uml.MessageSort.synchCall):
            with self.assertRaises(OperationResultError): self.result(message, 'Message', 'messageKind', value)

    def test_unlimited_and_real_domains_are_checked_on_results(self):
        value = Uml.LiteralUnlimitedNatural()
        self.assertEqual(self.result(value, 'LiteralUnlimitedNatural', 'unlimitedValue', float('inf')), float('inf'))
        for result in (-1, 1.5, True, float('nan'), float('-inf')):
            with self.assertRaises(OperationResultError): self.result(value, 'LiteralUnlimitedNatural', 'unlimitedValue', result)
        real = Uml.LiteralReal(value=1.5)
        for result in (float('nan'), float('inf'), True):
            with self.assertRaises(OperationResultError): self.result(real, 'LiteralReal', 'realValue', result)
        self.assertEqual(self.result(real, 'LiteralReal', 'realValue', 2), 2)

    def test_argument_collections_enforce_uniqueness_before_query_runs(self):
        package, cls = Uml.Package(), Uml.Class()
        with patch.dict(OPERATIONS, {'Namespace.excludeCollisions': lambda *args, **kwargs: self.fail('Body must not run')}):
            with self.assertRaises(ValueError): package.excludeCollisions([cls, cls])
            with self.assertRaises(TypeError): package.excludeCollisions([None])

    def test_missing_literal_value_is_an_invalid_required_result(self):
        with self.assertRaises(OperationResultError): Uml.LiteralReal().realValue()
        self.assertIn(('multiplicity', 'LiteralReal-value'), Uml.LiteralReal().validate())

    @verifies('NamedElement.qualifiedName', 'LiteralString.stringValue', 'ElementImport.getName', 'Namespace.getNamesOfMember')
    def test_nullable_source_inconsistencies_have_narrow_explicit_interpretations(self):
        self.assertIsNone(Uml.Class().uml_operation('NamedElement', 'qualifiedName'))
        self.assertIsNone(Uml.LiteralString().stringValue())
        element = Uml.Class()
        self.assertIsNone(Uml.ElementImport(importedElement=element).getName())
        package = Uml.Package(packagedElement=[element])
        self.assertEqual(package.getNamesOfMember(element), [None])
        with self.assertRaises(OperationResultError): self.result(element, 'NamedElement', 'separator', None)
