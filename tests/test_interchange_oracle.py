"""The authored structural oracle must detect deliberate model corruption."""
import unittest
from scripts.verify_independent_xmi import EXPECTED, VERSIONS, fixture, snapshot
from umltools.xmi import loads


class OracleCases(unittest.TestCase):
    def test_authored_fixture_roundtrip_and_corruption_controls(self):
        for version in VERSIONS:
            doc = fixture(version)
            self.assertEqual(snapshot(doc.session.elements), EXPECTED)
            restored = loads(doc.dumps(), semantic_version='auto')
            self.assertEqual(snapshot(restored.session.elements), EXPECTED)
            named = {getattr(e, 'name', None): e for e in restored.session.elements}
            named['high'].value = 5
            self.assertNotEqual(snapshot(restored.session.elements), EXPECTED)
            named['high'].value = 4
            named['connection'].end.reverse()
            self.assertNotEqual(snapshot(restored.session.elements), EXPECTED)
            named['connection'].end.reverse()
            named['input'].type = named['Base']
            self.assertNotEqual(snapshot(restored.session.elements), EXPECTED)
            named['input'].type = named['Service']
            restored.move(named['part'], owner=named['Base'], feature='ownedAttribute')
            self.assertNotEqual(snapshot(restored.session.elements), EXPECTED)
