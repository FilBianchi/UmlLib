import unittest
from semantic_report import report


class ReportCases(unittest.TestCase):
    def test_matrix_preserves_contracts_conditions_and_unresolved_sources(self):
        result = report()
        records = {r['id']: r for r in result['definitions']}
        self.assertEqual(records['LiteralInteger-value']['type'], 'Integer')
        self.assertEqual(records['LiteralInteger-value']['lower'], 1)
        self.assertEqual(records['OpaqueExpression-isPositive-pre']['kind'], 'precondition')
        self.assertTrue(records['OpaqueExpression-isPositive-pre']['expressions'])
        self.assertEqual(records['OpaqueExpression-result.1']['review'], 'source inconsistency')
        self.assertEqual(records['PackageMerge']['review'], 'partial')
        self.assertEqual(records['ProfileApplication-isStrict']['review'], 'partial')
        self.assertEqual(result['duplicate_source_ids']['State-isConsistentWith'], 2)
        vertex = next(r for r in result['definitions'] if r.get('name') == 'Vertex.isConsistentWith')
        self.assertTrue(vertex['source_id_ambiguous'])
        self.assertIn('redefinedElement.oclIsKindOf(Vertex)', vertex['body_conditions'][0]['expressions'][0]['body'])
        for package in ('CommonStructure', 'Values', 'Classification', 'SimpleClassifiers', 'Packages', 'StructuredClassifiers', 'CommonBehavior', 'StateMachines', 'Activities', 'Actions', 'Interactions', 'UseCases', 'Deployments', 'InformationFlows'):
            self.assertEqual(result['package_audit'][package]['invariants'], result['package_audit'][package]['invariants_with_examples'])
            for category in ('operation', 'derived property', 'precondition'):
                counts = result['package_audit'][package]['definitions'][category]
                self.assertEqual(counts['declared'], counts['with_examples'])

    def test_linked_examples_resolve_to_existing_rules_and_test_methods(self):
        records = {r.get('name'): r for r in report()['definitions']}
        for identifier in ('InformationFlow.must_conform', 'PartDecomposition.assume',
                           'Stereotype.base_property_multiplicity_multiple_extension', 'Profile.references_same_metamodel'):
            self.assertEqual(records[identifier]['verification'], 'linked behavioral examples')
        for record in report()['definitions']:
            for test in record['tests']:
                module, cls, method = test.split('.')
                imported = __import__(module)
                self.assertTrue(callable(getattr(getattr(imported, cls), method)))
        self.assertEqual(records['Activity.maximum_one_parameter_node']['verification'], 'linked behavioral examples')
        self.assertEqual(records['ObjectFlow.target']['review'], 'context dependent')
        self.assertEqual(records['ObjectFlow.transformation_behavior']['review'], 'partial')
        self.assertEqual(records['ActionInputPin.no_control_or_object_flow']['review'], 'source inconsistency')
        self.assertEqual(records['Gate.getOperand']['review'], 'source inconsistency')
        self.assertEqual(records['Message.signature_is_operation_reply']['review'], 'partial')
        self.assertEqual(records['Node.internal_structure']['review'], 'source inconsistency')
        self.assertEqual(records['DeploymentTarget.deployedElement']['review'], 'partial')
