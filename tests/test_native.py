"""Behavioral examples for the manually translated specification definitions."""
import math
import unittest
from unittest.mock import patch
import Uml
from umltools import SPECIFICATIONS, UnsupportedSemanticsError
from umltools.native import OPERATIONS, CONSTRAINTS


class NativeRuntimeTests(unittest.TestCase):
    def test_registered_definitions_resolve_to_specification(self):
        for identifier in OPERATIONS:
            owner, name = identifier.split('.')
            self.assertIn(name, SPECIFICATIONS[owner].operations)
        for identifier in CONSTRAINTS:
            owner, name = identifier.split('.')
            self.assertIn(name, SPECIFICATIONS[owner].constraints)

    def test_model_queries_and_validation_do_not_interpret_ocl(self):
        model = Uml.Model(name='M')
        cls = Uml.Class(name='C')
        model.packagedElement.append(cls)
        with patch('umltools.ocl.evaluate', side_effect=AssertionError('OCL must not execute')):
            self.assertEqual(model.allOwnedElements(), [cls])
            self.assertEqual(cls.qualifiedName, 'M::C')
            self.assertEqual(Uml.Property().lower, 1)
            self.assertNotIn(('constraint', 'Element.has_owner'), cls.validate())
            self.assertNotIn(('constraint', 'Element.has_owner'), model.validate())

    def test_missing_registration_never_falls_back_to_interpreter(self):
        with patch('umltools.ocl.evaluate', side_effect=AssertionError('Unexpected fallback')):
            implementation = OPERATIONS.pop('Classifier.conformsTo')
            try:
                with self.assertRaises(UnsupportedSemanticsError):
                    Uml.Class().conformsTo(Uml.Class())
            finally:
                OPERATIONS['Classifier.conformsTo'] = implementation

    def test_operation_argument_binding_and_types(self):
        classifier = Uml.Class()
        with self.assertRaises(TypeError): classifier.conformsTo('not a UML Type')
        with self.assertRaises(TypeError): classifier.conformsTo(classifier, other=classifier)
        with self.assertRaises(TypeError): classifier.conformsTo(unknown=classifier)
        with self.assertRaises(TypeError): classifier.conformsTo()
        self.assertTrue(classifier.conformsTo(other=classifier))


class NativeNamingTests(unittest.TestCase):
    def test_missing_names_and_duplicate_members(self):
        package = Uml.Package(name='P')
        one, two = Uml.Class(name='C'), Uml.Class(name='C')
        package.packagedElement.extend([one, two])
        self.assertIn(('constraint', 'Namespace.members_distinguishable'), package.validate())
        two.name = 'D'
        self.assertNotIn(('constraint', 'Namespace.members_distinguishable'), package.validate())
        package.name = None
        self.assertIsNone(one.qualifiedName)
        self.assertEqual(one.allNamespaces(), [package])

    def test_import_alias_and_collision(self):
        source, destination = Uml.Package(name='Source'), Uml.Package(name='Destination')
        one, two = Uml.Class(name='C'), Uml.Class(name='C')
        source.packagedElement.extend([one, two])
        destination.elementImport.append(Uml.ElementImport(importedElement=one, alias='First'))
        destination.elementImport.append(Uml.ElementImport(importedElement=two, alias='Second'))
        self.assertEqual(destination.getNamesOfMember(one), ['First'])
        self.assertEqual(destination.importedMember, [one, two])
        destination.elementImport[1].alias = 'First'
        self.assertEqual(destination.importedMember, [])

    def test_public_reexport_and_private_filter(self):
        source, destination = Uml.Package(), Uml.Package()
        public = Uml.Class(name='Public', visibility=Uml.VisibilityKind.public)
        private = Uml.Class(name='Private', visibility=Uml.VisibilityKind.private)
        source.packagedElement.extend([public, private])
        destination.packageImport.append(Uml.PackageImport(importedPackage=source))
        self.assertEqual(source.visibleMembers(), [public])
        self.assertEqual(destination.visibleMembers(), [public])
        destination.packageImport[0].visibility = Uml.VisibilityKind.private
        self.assertEqual(destination.importedMember, [public])
        self.assertEqual(destination.visibleMembers(), [])


class NativeInheritanceTests(unittest.TestCase):
    def test_diamond_inheritance_and_visibility(self):
        base, left, right, leaf = [Uml.Class(name=name) for name in ('Base', 'Left', 'Right', 'Leaf')]
        left.generalization.append(Uml.Generalization(general=base))
        right.generalization.append(Uml.Generalization(general=base))
        leaf.generalization.extend([Uml.Generalization(general=left), Uml.Generalization(general=right)])
        public = Uml.Property(name='public', visibility=Uml.VisibilityKind.public)
        private = Uml.Property(name='private', visibility=Uml.VisibilityKind.private)
        base.ownedAttribute.extend([public, private])
        self.assertEqual(set(leaf.allParents()), {base, left, right})
        self.assertTrue(leaf.conformsTo(base))
        self.assertFalse(base.conformsTo(leaf))
        self.assertIn(public, leaf.member)
        self.assertNotIn(private, leaf.member)
        self.assertEqual(leaf.allAttributes(), [public])
        self.assertIs(public.featuringClassifier, base)

    def test_cycles_terminate_and_fail_invariant(self):
        one, two = Uml.Class(), Uml.Class()
        one.generalization.append(Uml.Generalization(general=two))
        two.generalization.append(Uml.Generalization(general=one))
        self.assertIn(one, one.allParents())
        self.assertIn(('constraint', 'Classifier.no_cycles_in_generalization'), one.validate())

    def test_final_parent_and_redefinition_bounds(self):
        base, child = Uml.Class(isFinalSpecialization=True), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        self.assertIn(('constraint', 'Classifier.non_final_parents'), child.validate())
        type_ = Uml.Class(name='T')
        original = Uml.Property(name='x', type=type_, upperValue=Uml.LiteralUnlimitedNatural(value=3))
        replacement = Uml.Property(name='x', type=type_, upperValue=Uml.LiteralUnlimitedNatural(value=2), redefinedProperty=[original])
        base.ownedAttribute.append(original)
        child.ownedAttribute.append(replacement)
        self.assertTrue(original.isConsistentWith(replacement))
        replacement.upperValue.value = 4
        self.assertFalse(original.isConsistentWith(replacement))


class NativeMultiplicityTests(unittest.TestCase):
    def test_literal_defaults_and_optional_queries(self):
        self.assertIsNone(Uml.LiteralString().stringValue())
        self.assertEqual(Uml.LiteralString(value='').stringValue(), '')
        self.assertEqual(Uml.LiteralInteger().integerValue(), 0)
        self.assertFalse(Uml.LiteralBoolean().booleanValue())
        self.assertTrue(Uml.LiteralNull().isNull())
        self.assertIsNone(Uml.LiteralString(value='x').integerValue())

    def test_unbounded_multiplicity(self):
        broad = Uml.Property(lowerValue=Uml.LiteralInteger(value=0), upperValue=Uml.LiteralUnlimitedNatural(value=math.inf))
        narrow = Uml.Property(lowerValue=Uml.LiteralInteger(value=1), upperValue=Uml.LiteralUnlimitedNatural(value=5))
        self.assertEqual(broad.upper, math.inf)
        self.assertTrue(broad.includesMultiplicity(narrow))
        self.assertTrue(narrow.compatibleWith(broad))
        self.assertFalse(broad.compatibleWith(narrow))
        self.assertTrue(broad.isMultivalued())
        self.assertTrue(narrow.is_(1, 5))
        with self.assertRaises(ValueError): Uml.LiteralUnlimitedNatural(value=-1)

    def test_invalid_bound_and_extension_default(self):
        prop = Uml.Property(lowerValue=Uml.LiteralInteger(value=2), upperValue=Uml.LiteralUnlimitedNatural(value=1))
        self.assertIn(('constraint', 'MultiplicityElement.upper_ge_lower'), prop.validate())
        self.assertEqual(Uml.ExtensionEnd().lower, 0)
        bad = Uml.Property(lowerValue=Uml.LiteralString(value='two'))
        self.assertIn(('constraint', 'MultiplicityElement.lower_is_integer'), bad.validate())


class NativeStateMachineTests(unittest.TestCase):
    def make_machine(self):
        machine = Uml.StateMachines.StateMachine(name='Machine')
        region = Uml.StateMachines.Region()
        machine.region.append(region)
        first, second = Uml.StateMachines.State(name='A'), Uml.StateMachines.FinalState(name='B')
        region.subvertex.extend([first, second])
        transition = Uml.StateMachines.Transition(source=first, target=second)
        region.transition.append(transition)
        return machine, region, first, second, transition

    def test_machine_membership_and_incoming_outgoing(self):
        machine, region, first, second, transition = self.make_machine()
        self.assertIs(first.containingStateMachine(), machine)
        self.assertIs(transition.containingStateMachine(), machine)
        self.assertEqual(first.outgoing, [transition])
        self.assertEqual(second.incoming, [transition])
        self.assertTrue(first.isSimple)
        self.assertIs(machine.LCA(first, second), region)
        self.assertNotIn(('constraint', 'Transition.transition_vertices'), transition.validate())

    def test_nested_orthogonal_states(self):
        machine, top, outer, other, transition = self.make_machine()
        left, right = Uml.Region(), Uml.Region()
        outer.region.extend([left, right])
        one, two = Uml.State(), Uml.State()
        left.subvertex.append(one)
        right.subvertex.append(two)
        self.assertTrue(outer.isComposite)
        self.assertTrue(outer.isOrthogonal)
        self.assertTrue(one.isContainedInState(outer))
        self.assertTrue(one.isContainedInRegion(top))
        self.assertTrue(machine.ancestor(one, outer))
        self.assertFalse(machine.ancestor(outer, one))
        self.assertIs(machine.LCAState(one, two), outer)
        self.assertIs(machine.LCA(one, two), top)

    def test_internal_transition_and_final_state_failures(self):
        machine, region, first, second, transition = self.make_machine()
        transition.kind = Uml.TransitionKind.internal
        self.assertIn(('constraint', 'Transition.state_is_internal'), transition.validate())
        transition.target = first
        self.assertNotIn(('constraint', 'Transition.state_is_internal'), transition.validate())
        illegal = Uml.Transition(source=second, target=first)
        region.transition.append(illegal)
        self.assertIn(('constraint', 'FinalState.no_outgoing_transitions'), second.validate())

    def test_initial_vertex_count_changes(self):
        machine, region, first, second, transition = self.make_machine()
        region.subvertex.extend([Uml.Pseudostate(), Uml.Pseudostate()])
        self.assertIn(('constraint', 'Region.initial_vertex'), region.validate())
        region.subvertex[-1].kind = Uml.PseudostateKind.choice
        self.assertNotIn(('constraint', 'Region.initial_vertex'), region.validate())

    def test_orthogonal_fork_uses_distinct_transition_pairs(self):
        machine, top, outer, start, unused = self.make_machine()
        left, right = Uml.Region(), Uml.Region()
        outer.region.extend([left, right])
        one, two = Uml.State(), Uml.State()
        left.subvertex.append(one)
        right.subvertex.append(two)
        fork = Uml.Pseudostate(kind=Uml.PseudostateKind.fork)
        top.subvertex.append(fork)
        branch_one = Uml.Transition(source=fork, target=one)
        branch_two = Uml.Transition(source=fork, target=two)
        top.transition.extend([Uml.Transition(source=start, target=fork), branch_one, branch_two])
        self.assertNotIn(('constraint', 'Pseudostate.transitions_outgoing'), fork.validate())
        branch_two.target = one
        self.assertIn(('constraint', 'Pseudostate.transitions_outgoing'), fork.validate())
