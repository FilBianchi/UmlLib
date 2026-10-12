"""Packages scenarios traced to UML XMI declarations and their descriptions."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check
from semantic_cases import verifies


class PackageCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    @verifies('Package.nestedPackage', 'Package.ownedType', 'Package.ownedStereotype', 'Package.allApplicableStereotypes', 'Package.mustBeOwned')
    def test_owned_package_type_and_stereotype_filters_and_recursive_collection(self):
        outer, nested, deepest = Uml.Package(), Uml.Package(), Uml.Profile()
        first, second = Uml.Stereotype(name='First'), Uml.Stereotype(name='Second')
        type_, unrelated = Uml.Class(), Uml.Package()
        nested.packagedElement.extend([deepest, first])
        deepest.packagedElement.append(second)
        outer.packagedElement.extend([nested, type_])
        outer.packageImport.append(Uml.PackageImport(importedPackage=unrelated))
        self.assertEqual(list(outer.nestedPackage), [nested])
        self.assertEqual(list(outer.ownedType), [type_])
        self.assertEqual(list(nested.ownedStereotype), [first])
        self.assertEqual(set(outer.allApplicableStereotypes()), {first, second})
        self.assertFalse(outer.mustBeOwned())
        deepest.packagedElement.remove(second)
        unrelated.packagedElement.append(second)
        self.assertEqual(outer.allApplicableStereotypes(), [first])

    @verifies('Package.containingProfile', 'Stereotype.containingProfile', 'Stereotype.profile')
    def test_nearest_profile_and_containment_changes(self):
        outer, nested, inner = Uml.Profile(), Uml.Package(), Uml.Profile()
        outer.packagedElement.append(nested)
        nested.packagedElement.append(inner)
        stereotype = Uml.Stereotype()
        inner.packagedElement.append(stereotype)
        self.assertIs(nested.containingProfile(), outer)
        self.assertIs(stereotype.containingProfile(), inner)
        self.assertIs(stereotype.profile, inner)
        self.assertIs(inner.containingProfile(), inner)
        outer.packagedElement.remove(nested)
        self.assertIsNone(nested.containingProfile())
        with self.assertRaises(ValueError): Uml.Stereotype().containingProfile()

    @verifies('Package.elements_public_or_private', 'Package.makesVisible', 'Package.visibleMembers', 'Package-makesVisible-pre')
    def test_visible_members_public_private_imports_aliases_and_reexport(self):
        source, facade, consumer = Uml.Package(), Uml.Package(), Uml.Package()
        public, private, unspecified = Uml.Class(name='A'), Uml.Class(name='B', visibility=Uml.VisibilityKind.private), Uml.Class(name='C', visibility=None)
        source.packagedElement.extend([public, private, unspecified])
        self.assertTrue(check(source, 'Package.elements_public_or_private'))
        self.assertEqual(set(source.visibleMembers()), {public, unspecified})
        self.assertFalse(source.makesVisible(private))
        public.visibility = Uml.VisibilityKind.protected
        self.assertFalse(check(source, 'Package.elements_public_or_private'))
        public.visibility = Uml.VisibilityKind.public
        facade.elementImport.append(Uml.ElementImport(importedElement=public, alias='Alias', visibility=Uml.VisibilityKind.private))
        self.assertIn(public, facade.member)
        self.assertEqual(facade.visibleMembers(), [])
        facade.elementImport[0].visibility = Uml.VisibilityKind.public
        consumer.packageImport.append(Uml.PackageImport(importedPackage=facade))
        self.assertEqual(consumer.visibleMembers(), [public])
        self.assertEqual(consumer.getNamesOfMember(public), ['Alias'])
        consumer.packageImport[0].visibility = Uml.VisibilityKind.private
        self.assertIn(public, consumer.member)
        self.assertEqual(consumer.visibleMembers(), [])
        with self.assertRaises(ValueError): consumer.makesVisible(private)

    def extension(self, profile, stereotype, metaclass, *, lower=0):
        prop = Uml.Property(name='base_' + (metaclass.name or 'M'), type=metaclass)
        end = Uml.ExtensionEnd(type=stereotype, aggregation=Uml.AggregationKind.composite)
        end.lowerValue = Uml.LiteralInteger(value=lower)
        extension = Uml.Extension(ownedEnd=end, memberEnd=[prop, end])
        stereotype.ownedAttribute.append(prop)
        profile.packagedElement.append(extension)
        return extension, prop, end

    @verifies('Extension.isRequired', 'Extension.metaclass', 'Extension.metaclassEnd', 'Extension.non_owned_end',
              'Extension.is_binary', 'ExtensionEnd.lowerBound', 'ExtensionEnd.multiplicity', 'ExtensionEnd.aggregation', 'ExtensionEnd-lower')
    def test_extension_end_roles_required_flag_defaults_and_invalid_arity(self):
        profile, stereotype, meta = Uml.Profile(), Uml.Stereotype(), Uml.Class(name='Class')
        profile.packagedElement.append(stereotype)
        extension, prop, end = self.extension(profile, stereotype, meta)
        self.assertIs(extension.metaclassEnd(), prop)
        self.assertIs(extension.metaclass, meta)
        self.assertFalse(extension.isRequired)
        self.assertEqual(Uml.ExtensionEnd().lowerBound(), 0)
        self.assertEqual(Uml.ExtensionEnd().lower, 0)
        self.assertTrue(check(extension, 'Extension.non_owned_end'))
        self.assertTrue(check(extension, 'Extension.is_binary'))
        self.assertTrue(check(end, 'ExtensionEnd.multiplicity'))
        end.lowerValue.value = 1
        self.assertTrue(extension.isRequired)
        end.lowerValue.value = 2
        self.assertFalse(check(end, 'ExtensionEnd.multiplicity'))
        end.aggregation = Uml.AggregationKind.none
        self.assertFalse(check(end, 'ExtensionEnd.aggregation'))
        prop.type = Uml.Interface()
        self.assertFalse(check(extension, 'Extension.non_owned_end'))
        extension.memberEnd.append(Uml.Property(type=meta))
        self.assertFalse(check(extension, 'Extension.is_binary'))
        with self.assertRaises(ValueError): extension.metaclassEnd()

    @verifies('Profile.references_same_metamodel', 'Profile.metaclass_reference_not_specialized')
    def test_profile_references_need_one_root_and_no_specialization_across_the_boundary(self):
        profile, root, other_root = Uml.Profile(), Uml.Model(), Uml.Model()
        meta, other = Uml.Class(), Uml.Class()
        root.packagedElement.append(meta)
        other_root.packagedElement.append(other)
        profile.metaclassReference.append(Uml.ElementImport(importedElement=meta))
        self.assertTrue(check(profile, 'Profile.references_same_metamodel'))
        profile.metaclassReference.append(Uml.ElementImport(importedElement=other))
        self.assertFalse(check(profile, 'Profile.references_same_metamodel'))
        profile.metaclassReference.pop()
        local = Uml.Stereotype()
        profile.packagedElement.append(local)
        self.assertTrue(check(profile, 'Profile.metaclass_reference_not_specialized'))
        meta.generalization.append(Uml.Generalization(general=local))
        self.assertFalse(check(profile, 'Profile.metaclass_reference_not_specialized'))
        meta.generalization.clear()
        local.generalization.append(Uml.Generalization(general=meta))
        self.assertFalse(check(profile, 'Profile.metaclass_reference_not_specialized'))

    @verifies('Stereotype.generalize', 'Stereotype.name_not_clash', 'Stereotype.binaryAssociationsOnly', 'Stereotype.associationEndOwnership')
    def test_stereotype_generalization_keywords_and_association_end_ownership(self):
        profile, stereotype = Uml.Profile(), Uml.Stereotype(name='Domain')
        profile.packagedElement.append(stereotype)
        extension, base, end = self.extension(profile, stereotype, Uml.Class(name='Class'))
        self.assertTrue(check(stereotype, 'Stereotype.generalize'))
        stereotype.generalization.append(Uml.Generalization(general=Uml.Class()))
        self.assertFalse(check(stereotype, 'Stereotype.generalize'))
        stereotype.generalization.clear()
        invalid_child = Uml.Class(generalization=[Uml.Generalization(general=stereotype)])
        self.assertFalse(check(stereotype, 'Stereotype.generalize'))
        invalid_child.generalization.clear()
        stereotype.name = 'CLASS'
        self.assertFalse(check(stereotype, 'Stereotype.name_not_clash'))
        stereotype.name = 'Domain'
        normal_type, attribute, opposite = Uml.Class(), Uml.Property(), Uml.Property(type=stereotype)
        attribute.type = normal_type
        association = Uml.Association(ownedEnd=[opposite], memberEnd=[attribute, opposite])
        stereotype.ownedAttribute.append(attribute)
        self.assertTrue(check(stereotype, 'Stereotype.binaryAssociationsOnly'))
        self.assertTrue(check(stereotype, 'Stereotype.associationEndOwnership'))
        association.ownedEnd.remove(opposite)
        normal_type.ownedAttribute.append(opposite)
        self.assertFalse(check(stereotype, 'Stereotype.associationEndOwnership'))
        association.memberEnd.append(Uml.Property(type=normal_type))
        self.assertFalse(check(stereotype, 'Stereotype.binaryAssociationsOnly'))

    @verifies('Stereotype.base_property_upper_bound', 'Stereotype.base_property_multiplicity_single_extension',
              'Stereotype.base_property_multiplicity_multiple_extension')
    def test_one_vs_multiple_extension_base_multiplicities(self):
        profile, stereotype = Uml.Profile(), Uml.Stereotype()
        profile.packagedElement.append(stereotype)
        first, prop, end = self.extension(profile, stereotype, Uml.Class(name='Class'))
        self.assertTrue(check(stereotype, 'Stereotype.base_property_multiplicity_single_extension'))
        prop.lowerValue = Uml.LiteralInteger(value=0)
        self.assertFalse(check(stereotype, 'Stereotype.base_property_multiplicity_single_extension'))
        second, other, _ = self.extension(profile, stereotype, Uml.Class(name='State'))
        self.assertFalse(check(stereotype, 'Stereotype.base_property_multiplicity_multiple_extension'))
        other.lowerValue = Uml.LiteralInteger(value=0)
        self.assertTrue(check(stereotype, 'Stereotype.base_property_multiplicity_multiple_extension'))
        other.upperValue = Uml.LiteralUnlimitedNatural(value=2)
        self.assertFalse(check(stereotype, 'Stereotype.base_property_upper_bound'))

    @verifies('PackageMerge-mergedPackage', 'PackageMerge-receivingPackage', 'ProfileApplication-appliedProfile', 'ProfileApplication-applyingPackage')
    def test_merge_and_profile_application_links_preserve_identity_and_ownership(self):
        source, receiver, profile = Uml.Package(), Uml.Package(), Uml.Profile()
        merge = Uml.PackageMerge(mergedPackage=source)
        application = Uml.ProfileApplication(appliedProfile=profile)
        receiver.packageMerge.append(merge)
        receiver.profileApplication.append(application)
        self.assertIs(merge.receivingPackage, receiver)
        self.assertIs(merge.mergedPackage, source)
        self.assertIs(application.applyingPackage, receiver)
        self.assertIs(application.appliedProfile, profile)
        source.delete()
        self.assertIsNone(merge.mergedPackage)
        self.assertIn(('multiplicity', 'PackageMerge-mergedPackage'), merge.validate())
