"""Keep the declaration inventory independent of the registry being counted."""
import unittest
from scripts.report_uml241_complete_audit import audit


class AuditInventory241Cases(unittest.TestCase):
    def test_all_source_declarations_have_scoped_implementations(self):
        report=audit()
        self.assertEqual(report['counts'],{'operation':150,'constraint':433,'derived property':74})
        self.assertEqual(report['structural_counts'],{'association-owned property':328,'stored property':550,'derived property':74})
        self.assertEqual(report['stored_setters_swept'],549)
        self.assertEqual(len(report['families']),14)
        self.assertTrue(all(r['implementation'] for r in report['records']))
