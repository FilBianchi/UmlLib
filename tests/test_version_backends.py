"""Use both normative metamodels in one process without mixing their contracts."""
import unittest
import subprocess
import sys
import Uml
import Uml241 as old
import Uml251 as new


class BackendCases(unittest.TestCase):
    def test_backend_can_bootstrap_before_the_generated_facade(self):
        result=subprocess.run([sys.executable,'-c',
            "from umltools.version_backend import backend_241; b=backend_241(); import Uml241,Uml251; assert len(b.SPECIFICATIONS)==242; assert Uml241.Class().semantic_version=='2.4.1'; assert Uml251.Class().semantic_version=='2.5.1'"],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_independent_types_versions_and_alias_compatibility(self):
        self.assertEqual(len(old._classes.__all__),255)
        self.assertIs(new.Class,Uml.Class)
        self.assertIsNot(old.Class,new.Class)
        self.assertEqual(old.Class().semantic_version,'2.4.1')
        self.assertEqual(new.Class().semantic_version,'2.5.1')
        self.assertIs(old.StateMachine.State,old.State)
        self.assertIsNot(old.VisibilityKind,new.VisibilityKind)
        self.assertNotIsInstance(old.Pseudostate(),old.RedefinableElement)
        self.assertIsInstance(new.Pseudostate(),new.RedefinableElement)

    def test_version_specific_cardinalities_and_stored_relation_metadata(self):
        self.assertIsNone(old.Feature.properties()['featuringClassifier'].upper)
        self.assertEqual(new.Feature.properties()['featuringClassifier'].upper,1)
        self.assertEqual(old.ActivityEdge.properties()['guard'].lower,1)
        self.assertEqual(new.ActivityEdge.properties()['guard'].lower,0)
        self.assertEqual(old.Class.properties()['ownedAttribute'].subsets,('Classifier-attribute','Namespace-ownedMember'))
        self.assertIn('redefinedState',old.State.properties())
        self.assertNotIn('redefinedVertex',old.Vertex.properties())

    def test_cross_version_reference_and_enum_assignment_fail_atomically(self):
        item=old.Property(type=old.Class())
        original=item.type
        with self.assertRaises(TypeError):item.type=new.Class()
        self.assertIs(item.type,original)
        with self.assertRaises(TypeError):old.Class(visibility=new.VisibilityKind.public)
        with self.assertRaises(TypeError):new.Property(type=old.Class())

    def test_session_isolation_and_rollback(self):
        with old.ModelSession() as old_session, new.ModelSession() as new_session:
            a=old.Class();b=new.Class()
            self.assertEqual(old_session.elements,{a})
            self.assertEqual(new_session.elements,{b})
            with self.assertRaises(TypeError):old.Class(ownedAttribute=[new.Property()])
            self.assertEqual(old_session.elements,{a})

    def test_loop_variable_ownership_differs_and_deletion_respects_it(self):
        with old.ModelSession(),new.ModelSession():
            a=old.OutputPin();b=new.OutputPin()
            old_loop=old.LoopNode(loopVariable=[a])
            new_loop=new.LoopNode(loopVariable=[b])
            self.assertIsNone(a.owner)
            self.assertIs(b.owner,new_loop)
            old_loop.delete();new_loop.delete()
            self.assertFalse(a.is_deleted)
            self.assertTrue(b.is_deleted)

    def test_reviewed_literal_and_bound_queries_and_unreviewed_operations(self):
        self.assertEqual(old.LiteralInteger(value=7).integerValue(),7)
        self.assertEqual(old.Property().lowerBound(),1)
        self.assertEqual(old.Property(upperValue=old.LiteralUnlimitedNatural(value=float('inf'))).upperBound(),float('inf'))
        self.assertEqual(old.Class().allParents(),[])
        self.assertEqual(new.Class().allParents(),[])
        issues=old.Class().validate()
        self.assertIn(('unsupported version contract','UML2.4.1.prose'),issues)

    def test_incomplete_profile_contract_and_versioned_exchange_are_explicit(self):
        from Uml241._runtime import engine
        document=engine.xmi.loads(engine.xmi.dumps(old.Model()))
        self.assertIsInstance(document.roots[0],old.Model)
        self.assertEqual(document.semantic_version,'2.4.1')
        with self.assertRaises(old.UnsupportedSemanticsError):engine.stereotypes.apply_profile(old.Model(),old.Profile())
        from umltools.native import check
        from umltools.semantics import derive
        with self.assertRaises(TypeError):check(old.Class(),'Element.has_owner')
        with self.assertRaises(TypeError):derive(old.Class(),old.Class.properties()['owner'])
