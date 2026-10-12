import unittest
import Uml
from umltools import ModelSession
from umltools.native import check
from umltools.stereotypes import apply_stereotype, applications, apply_profile, unapply_profile
from semantic_cases import verifies


class StereotypeCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()
        self.profile = Uml.Profile(name='Domain')
        self.metamodel = Uml.Model(name='UML')
        self.model = Uml.Model(name='M', profileApplication=[Uml.ProfileApplication(appliedProfile=self.profile)])
        self.element = Uml.Class(name='C')
        self.model.packagedElement.append(self.element)

    def tearDown(self): self.scope.__exit__(None, None, None)

    def define(self, names=('Class',), *, required=False, name='DomainClass'):
        stereotype = Uml.Stereotype(name=name, visibility=Uml.VisibilityKind.public)
        self.profile.packagedElement.append(stereotype)
        props = []
        for meta_name in names:
            metaclass = Uml.Class(name=meta_name)
            self.metamodel.packagedElement.append(metaclass)
            self.profile.metaclassReference.append(Uml.ElementImport(importedElement=metaclass))
            prop = Uml.Property(name='base_' + meta_name, type=metaclass,
                                lowerValue=Uml.LiteralInteger(value=1 if len(names) == 1 else 0),
                                upperValue=Uml.LiteralUnlimitedNatural(value=1))
            end = Uml.ExtensionEnd(type=stereotype, aggregation=Uml.AggregationKind.composite,
                                   lowerValue=Uml.LiteralInteger(value=1 if required else 0))
            extension = Uml.Extension(ownedEnd=end, memberEnd=[prop, end])
            self.profile.packagedElement.append(extension)
            stereotype.ownedAttribute.append(prop)
            props.append(prop)
        return stereotype, props

    @verifies('Stereotype.base_property_upper_bound', 'Stereotype.base_property_multiplicity_single_extension')
    def test_single_extension_definition_and_runtime_base_link(self):
        stereotype, props = self.define()
        app = apply_stereotype(self.element, stereotype)
        self.assertEqual(dict(app.base_slots), {props[0]: self.element})
        self.assertEqual(app.validate(), [])
        self.assertEqual(applications(self.element), (app,))
        props[0].upperValue.value = 2
        self.assertFalse(check(stereotype, 'Stereotype.base_property_upper_bound'))
        self.assertIn(('stereotype application', 'Stereotype.base_property_upper_bound'), app.validate())
        props[0].upperValue.value = 1
        props[0].lowerValue.value = 0
        self.assertFalse(check(stereotype, 'Stereotype.base_property_multiplicity_single_extension'))
        with self.assertRaises(ValueError): apply_stereotype(Uml.Class(), stereotype)

    @verifies('Stereotype.base_property_multiplicity_multiple_extension')
    def test_multiple_extensions_have_exactly_one_read_only_runtime_base(self):
        stereotype, props = self.define(('Class', 'State'))
        app = apply_stereotype(self.element, stereotype)
        self.assertEqual(dict(app.base_slots), {props[0]: self.element, props[1]: None})
        with self.assertRaises(TypeError): app.base_slots[props[1]] = Uml.State()
        state = Uml.State()
        machine = Uml.StateMachines.StateMachine(region=[Uml.Region(subvertex=[state])])
        self.model.packagedElement.append(machine)
        app.rebind(state)
        self.assertEqual(dict(app.base_slots), {props[0]: None, props[1]: state})
        self.assertEqual(applications(self.element), ())
        self.assertEqual(applications(state), (app,))
        self.assertEqual(app.validate(), [])
        props[1].lowerValue.value = 1
        self.assertFalse(check(stereotype, 'Stereotype.base_property_multiplicity_multiple_extension'))

    def test_ambiguous_inherited_metaclasses_need_an_explicit_base(self):
        stereotype, props = self.define(('Class', 'NamedElement'))
        with self.assertRaises(ValueError): apply_stereotype(self.element, stereotype)
        self.assertEqual(applications(self.element), ())
        app = apply_stereotype(self.element, stereotype, base_property='base_Class')
        self.assertIs(app.base_slots[props[0]], self.element)
        self.assertIsNone(app.base_slots[props[1]])

    def test_wrong_metaclass_rebind_does_not_remove_original_application(self):
        stereotype, props = self.define()
        app = apply_stereotype(self.element, stereotype)
        package = Uml.Package()
        self.model.packagedElement.append(package)
        with self.assertRaises(ValueError): app.rebind(package)
        self.assertIs(app.element, self.element)
        self.assertEqual(applications(self.element), (app,))
        self.assertEqual(applications(package), ())

    def test_duplicate_stereotype_or_subtype_application_is_rejected(self):
        stereotype, props = self.define()
        child = Uml.Stereotype(name='Special', generalization=[Uml.Generalization(general=stereotype)])
        self.profile.packagedElement.append(child)
        app = apply_stereotype(self.element, child)
        self.assertEqual(app.base_slots[props[0]], self.element)
        with self.assertRaises(ValueError): apply_stereotype(self.element, stereotype)
        with self.assertRaises(ValueError): apply_stereotype(self.element, child)
        self.assertEqual(applications(self.element), (app,))

    def test_unrelated_stereotypes_can_coexist(self):
        first, _ = self.define(name='First')
        second, _ = self.define(name='Second')
        a, b = apply_stereotype(self.element, first), apply_stereotype(self.element, second)
        self.assertEqual(set(applications(self.element)), {a, b})

    def test_required_extension_is_checked_by_model_validation(self):
        stereotype, props = self.define(required=True)
        missing = ('stereotype application', 'Stereotype.required_extension')
        self.assertIn(missing, self.element.validate())
        app = apply_stereotype(self.element, stereotype)
        self.assertNotIn(missing, self.element.validate())
        app.detach()
        self.assertIn(missing, self.element.validate())

    def test_required_abstract_stereotype_is_satisfied_by_a_concrete_subtype(self):
        stereotype, props = self.define(required=True)
        stereotype.isAbstract = True
        child = Uml.Stereotype(name='Concrete', generalization=[Uml.Generalization(general=stereotype)])
        self.profile.packagedElement.append(child)
        with self.assertRaises(ValueError): apply_stereotype(self.element, stereotype)
        app = apply_stereotype(self.element, child)
        self.assertNotIn(('stereotype application', 'Stereotype.required_extension'), self.element.validate())

    def test_profile_must_be_applied_and_can_be_inherited_from_an_outer_package(self):
        stereotype, props = self.define()
        nested = Uml.Package()
        self.model.packagedElement.remove(self.element)
        nested.packagedElement.append(self.element)
        self.model.packagedElement.append(nested)
        app = apply_stereotype(self.element, stereotype)
        self.model.profileApplication.clear()
        self.assertIn(('stereotype application', 'Stereotype.profile_available'), self.element.validate())
        with self.assertRaises(ValueError): app.rebind(self.element)

    def test_imported_and_nested_profiles_are_available(self):
        stereotype, props = self.define()
        outer = Uml.Profile(packageImport=[Uml.PackageImport(importedPackage=self.profile)])
        self.model.profileApplication[0].appliedProfile = outer
        app = apply_stereotype(self.element, stereotype)
        self.assertEqual(app.validate(), [])
        app.detach()
        outer.packageImport.clear()
        outer.packagedElement.append(self.profile)
        app = apply_stereotype(self.element, stereotype)
        self.assertEqual(app.validate(), [])

    def test_private_stereotypes_are_not_available(self):
        stereotype, props = self.define()
        stereotype.visibility = Uml.VisibilityKind.private
        with self.assertRaises(ValueError): apply_stereotype(self.element, stereotype)
        stereotype.visibility = Uml.VisibilityKind.public
        app = apply_stereotype(self.element, stereotype)
        stereotype.visibility = Uml.VisibilityKind.private
        self.assertIn(('stereotype application', 'Stereotype.profile_available'), app.validate())

    def test_profile_api_creates_required_instances_and_removes_them(self):
        stereotype, _ = self.define(required=True)
        self.model.profileApplication.clear()
        apply_profile(self.model, self.profile)
        apps = applications(self.element)
        self.assertEqual(len(apps), 1)
        self.assertIs(apps[0].stereotype, stereotype)
        self.assertEqual(apps[0].validate(), [])
        unapply_profile(self.model, self.profile)
        self.assertEqual(applications(self.element), ())
        self.assertIsNone(apps[0].element)
        self.assertIs(self.element.owner, self.model)

    def test_profile_application_failure_rolls_back_required_instances(self):
        stereotype, _ = self.define(required=True)
        stereotype.isAbstract = True
        self.model.profileApplication.clear()
        before = set(self.scope.elements)
        with self.assertRaises(ValueError): apply_profile(self.model, self.profile)
        self.assertEqual(self.model.profileApplication, [])
        self.assertEqual(applications(self.element), ())
        self.assertEqual(self.scope.elements, before)

    def test_late_profile_application_failure_also_removes_earlier_created_instances(self):
        first, _ = self.define(required=True, name='A')
        second, _ = self.define(required=True, name='Z')
        second.isAbstract = True
        self.model.profileApplication.clear()
        with self.assertRaises(ValueError): apply_profile(self.model, self.profile)
        self.assertEqual(self.model.profileApplication, [])
        self.assertEqual(applications(self.element), ())

    def test_removal_preserves_instances_accessible_through_another_profile(self):
        stereotype, _ = self.define()
        app = apply_stereotype(self.element, stereotype)
        wrapper = Uml.Profile(packageImport=[Uml.PackageImport(importedPackage=self.profile)])
        apply_profile(self.model, wrapper)
        unapply_profile(self.model, self.profile)
        self.assertEqual(applications(self.element), (app,))
        self.assertEqual(app.validate(), [])

    @verifies('Stereotype.binaryAssociationsOnly', 'Stereotype.associationEndOwnership')
    def test_binary_associations_and_ownership_of_the_other_end(self):
        stereotype, _ = self.define()
        attribute = Uml.Property(type=self.element)
        other_end = Uml.Property(type=stereotype)
        association = Uml.Association(ownedEnd=[other_end], memberEnd=[attribute, other_end])
        stereotype.ownedAttribute.append(attribute)
        self.assertTrue(check(stereotype, 'Stereotype.binaryAssociationsOnly'))
        self.assertTrue(check(stereotype, 'Stereotype.associationEndOwnership'))
        association.ownedEnd.remove(other_end)
        self.element.ownedAttribute.append(other_end)
        self.assertFalse(check(stereotype, 'Stereotype.associationEndOwnership'))
        association.memberEnd.append(Uml.Property(type=self.element))
        self.assertFalse(check(stereotype, 'Stereotype.binaryAssociationsOnly'))

    @verifies('Stereotype.generalize')
    def test_stereotype_generalizations_do_not_cross_metaclass_boundaries(self):
        parent, _ = self.define()
        child = Uml.Stereotype(generalization=[Uml.Generalization(general=parent)])
        self.assertTrue(check(parent, 'Stereotype.generalize'))
        self.assertTrue(check(child, 'Stereotype.generalize'))
        bad = Uml.Class(generalization=[Uml.Generalization(general=parent)])
        self.assertFalse(check(parent, 'Stereotype.generalize'))
        bad.generalization.clear()
        child.generalization.append(Uml.Generalization(general=self.element))
        self.assertFalse(check(child, 'Stereotype.generalize'))

    @verifies('Profile.references_same_metamodel')
    def test_references_to_two_different_base_metamodels_are_rejected(self):
        stereotype, props = self.define(('Class', 'State'))
        self.assertTrue(check(self.profile, 'Profile.references_same_metamodel'))
        second = Uml.Model(name='OtherMetamodel')
        meta = props[1].type
        self.metamodel.packagedElement.remove(meta)
        second.packagedElement.append(meta)
        self.assertFalse(check(self.profile, 'Profile.references_same_metamodel'))
        self.profile.metaclassReference.pop()
        self.profile.metamodelReference.append(Uml.PackageImport(importedPackage=second))
        self.assertFalse(check(self.profile, 'Profile.references_same_metamodel'))

    @verifies('Stereotype.base_property_multiplicity_multiple_extension', 'Stereotype.base_property_upper_bound')
    def test_generic_instance_slots_cannot_bind_two_metaclass_instances(self):
        stereotype, props = self.define(('Class', 'State'))
        first = Uml.InstanceSpecification(classifier=[props[0].type])
        second = Uml.InstanceSpecification(classifier=[props[1].type])
        self.model.packagedElement.extend([first, second])
        app = Uml.InstanceSpecification(classifier=[stereotype], slot=[
            Uml.Slot(definingFeature=props[0], value=[Uml.InstanceValue(instance=first)]),
            Uml.Slot(definingFeature=props[1], value=[Uml.InstanceValue(instance=second)]),
        ])
        issue = ('stereotype application', 'Stereotype.base_property_multiplicity_multiple_extension')
        self.assertIn(issue, app.validate())
        app.slot[1].value.clear()
        self.assertNotIn(issue, app.validate())
        self.assertFalse(any(category == 'stereotype application' for category, _ in app.validate()))
        app.slot[0].value.append(Uml.InstanceValue(instance=first))
        self.assertIn(('stereotype application', 'Stereotype.base_property_upper_bound'), app.validate())

    def test_generic_stereotype_slot_rejects_an_incompatible_instance(self):
        stereotype, props = self.define()
        target = Uml.InstanceSpecification(classifier=[Uml.Class()])
        self.model.packagedElement.append(target)
        app = Uml.InstanceSpecification(classifier=[stereotype], slot=[
            Uml.Slot(definingFeature=props[0], value=[Uml.InstanceValue(instance=target)])])
        self.assertIn(('stereotype application', 'Stereotype.base_instance'), app.validate())

    def test_generic_stereotype_instances_satisfy_required_extension_and_reject_duplicates(self):
        stereotype, props = self.define(required=True)
        target = Uml.InstanceSpecification(classifier=[props[0].type])
        self.model.packagedElement.append(target)
        missing = ('stereotype application', 'Stereotype.required_extension')
        self.assertIn(missing, target.validate())
        first = Uml.InstanceSpecification(classifier=[stereotype], slot=[
            Uml.Slot(definingFeature=props[0], value=[Uml.InstanceValue(instance=target)])])
        self.assertNotIn(missing, target.validate())
        second = Uml.InstanceSpecification(classifier=[stereotype], slot=[
            Uml.Slot(definingFeature=props[0], value=[Uml.InstanceValue(instance=target)])])
        duplicate = ('stereotype application', 'Stereotype.duplicate_application')
        self.assertIn(duplicate, first.validate())
        self.assertIn(duplicate, second.validate())
        with self.assertRaises(ValueError): apply_stereotype(target, stereotype)

    def test_profile_removal_also_deletes_modeled_stereotype_instances(self):
        stereotype, props = self.define()
        target = Uml.InstanceSpecification(classifier=[props[0].type])
        app = Uml.InstanceSpecification(classifier=[stereotype], slot=[
            Uml.Slot(definingFeature=props[0], value=[Uml.InstanceValue(instance=target)])])
        self.model.packagedElement.extend([target, app])
        slot, value = app.slot[0], app.slot[0].value[0]
        unapply_profile(self.model, self.profile)
        self.assertIn(target, self.model.packagedElement)
        self.assertNotIn(app, self.model.packagedElement)
        self.assertTrue(app.is_deleted)
        self.assertTrue(slot.is_deleted)
        self.assertTrue(value.is_deleted)
        self.assertNotIn(app, self.scope.elements)

    def test_profile_removal_preserves_other_classifiers_and_deletes_only_profile_slots(self):
        stereotype, props = self.define()
        ordinary_feature = Uml.Property()
        ordinary = Uml.Class(ownedAttribute=[ordinary_feature])
        target = Uml.InstanceSpecification(classifier=[props[0].type])
        base_value = Uml.InstanceValue(instance=target)
        base_slot = Uml.Slot(definingFeature=props[0], value=[base_value])
        ordinary_slot = Uml.Slot(definingFeature=ordinary_feature, value=[Uml.LiteralInteger(value=1)])
        app = Uml.InstanceSpecification(classifier=[stereotype, ordinary], slot=[base_slot, ordinary_slot])
        self.model.packagedElement.extend([target, app])
        unapply_profile(self.model, self.profile)
        self.assertFalse(app.is_deleted)
        self.assertEqual(list(app.classifier), [ordinary])
        self.assertEqual(list(app.slot), [ordinary_slot])
        self.assertTrue(base_slot.is_deleted)
        self.assertTrue(base_value.is_deleted)
        self.assertFalse(ordinary_slot.is_deleted)

    @verifies('Profile.metaclass_reference_not_specialized')
    def test_imported_metaclasses_cannot_be_specialized_in_a_profile(self):
        stereotype, props = self.define()
        self.assertTrue(check(self.profile, 'Profile.metaclass_reference_not_specialized'))
        stereotype.generalization.append(Uml.Generalization(general=props[0].type))
        self.assertFalse(check(self.profile, 'Profile.metaclass_reference_not_specialized'))

    @verifies('Stereotype.name_not_clash')
    def test_keyword_clashes_are_case_insensitive(self):
        stereotype, props = self.define()
        for name in ('class', 'Class', 'CLASS'):
            stereotype.name = name
            self.assertFalse(check(stereotype, 'Stereotype.name_not_clash'))
        stereotype.name = 'Entity'
        self.assertTrue(check(stereotype, 'Stereotype.name_not_clash'))
