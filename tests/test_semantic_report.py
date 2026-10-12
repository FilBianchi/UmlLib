import unittest
from semantic_report import report


class ReportCases(unittest.TestCase):
    def test_linked_examples_resolve_to_existing_rules_and_test_methods(self):
        records = {r.get('name'): r for r in report()['definitions']}
        for identifier in ('InformationFlow.must_conform', 'PartDecomposition.assume',
                           'Stereotype.base_property_multiplicity_multiple_extension', 'Profile.references_same_metamodel'):
            self.assertEqual(records[identifier]['verification'], 'linked behavioral examples')
            for test in records[identifier]['tests']:
                module, cls, method = test.split('.')
                imported = __import__(module)
                self.assertTrue(callable(getattr(getattr(imported, cls), method)))
        self.assertEqual(records['Constraint.no_side_effects']['verification'], 'no linked behavioral examples')
