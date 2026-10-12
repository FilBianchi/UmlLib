"""CommonStructure examples derived from the vendored body/rule definitions."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.expression_semantics import register_expression_facts
from semantic_cases import verifies


class CommonStructureCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    @verifies('Element.has_owner', 'Element.not_own_self', 'Element.allOwnedElements', 'Element.mustBeOwned', 'Element-ownedElement', 'Element-owner')
    def test_composite_ownership_transitive_members_and_cycle_rejection(self):
        root, cls, prop = Uml.Model(), Uml.Class(), Uml.Property()
        self.assertTrue(cls.mustBeOwned())
        self.assertFalse(check(cls, 'Element.has_owner'))
        root.packagedElement.append(cls)
        cls.ownedAttribute.append(prop)
        self.assertTrue(check(cls, 'Element.has_owner'))
        self.assertEqual(root.allOwnedElements(), [cls, prop])
        self.assertTrue(check(root, 'Element.not_own_self'))
        with self.assertRaises(ValueError): root.packagedElement.append(root)
        self.assertEqual(root.allOwnedElements(), [cls, prop])
        cls.ownedAttribute.remove(prop)
        self.assertIsNone(prop.owner)
        self.assertNotIn(prop, root.allOwnedElements())

    @verifies('NamedElement.allNamespaces', 'NamedElement.allOwningPackages', 'NamedElement.qualifiedName',
              'NamedElement.separator', 'NamedElement.has_qualified_name', 'NamedElement.has_no_qualified_name', 'NamedElement-namespace')
    def test_namespace_order_and_nullable_qualified_names(self):
        root, nested, cls = Uml.Model(name='M'), Uml.Package(name='P'), Uml.Class(name='C')
        root.packagedElement.append(nested)
        nested.packagedElement.append(cls)
        self.assertEqual(cls.allNamespaces(), [nested, root])
        self.assertEqual(cls.allOwningPackages(), [nested, root])
        self.assertEqual(cls.qualifiedName, 'M::P::C')
        self.assertEqual(cls.separator(), '::')
        self.assertTrue(check(cls, 'NamedElement.has_qualified_name'))
        nested.name = None
        self.assertIsNone(cls.qualifiedName)
        self.assertTrue(check(cls, 'NamedElement.has_no_qualified_name'))
        nested.name = 'P'
        cls.name = None
        self.assertIsNone(cls.qualifiedName)
        self.assertTrue(check(cls, 'NamedElement.has_no_qualified_name'))
        attribute = Uml.Property(name='x')
        cls.ownedAttribute.append(attribute)
        self.assertEqual(attribute.allOwningPackages(), [])

    @verifies('NamedElement.visibility_needs_ownership', 'PackageableElement.namespace_needs_visibility')
    def test_visibility_requirements_distinguish_owner_and_namespace(self):
        cls = Uml.Class(visibility=Uml.VisibilityKind.public)
        parameter = Uml.ClassifierTemplateParameter(ownedParameteredElement=cls)
        self.assertIsNone(cls.namespace)
        self.assertFalse(check(cls, 'NamedElement.visibility_needs_ownership'))
        cls.visibility = None
        self.assertTrue(check(cls, 'NamedElement.visibility_needs_ownership'))
        package, member = Uml.Package(), Uml.Class(visibility=None)
        package.packagedElement.append(member)
        self.assertFalse(check(member, 'PackageableElement.namespace_needs_visibility'))
        member.visibility = Uml.VisibilityKind.public
        self.assertTrue(check(member, 'PackageableElement.namespace_needs_visibility'))

    @verifies('NamedElement.clientDependency')
    def test_dependency_extent_and_changes_are_reflected_in_the_derived_property(self):
        client, supplier = Uml.Class(), Uml.Class()
        dependency = Uml.Dependency(client=[client], supplier=[supplier])
        self.assertEqual(client.clientDependency, [dependency])
        self.assertEqual(supplier.clientDependency, [])
        dependency.client.clear()
        self.assertEqual(client.clientDependency, [])

    @verifies('ElementImport.getName', 'ElementImport.imported_element_is_public', 'ElementImport.visibility_public_or_private', 'PackageImport.public_or_private')
    def test_import_alias_visibility_and_public_target(self):
        target = Uml.Class(name='Original', visibility=Uml.VisibilityKind.public)
        imp = Uml.ElementImport(importedElement=target)
        self.assertEqual(imp.getName(), 'Original')
        imp.alias = ''
        self.assertEqual(imp.getName(), '')
        imp.alias = 'Alias'
        self.assertEqual(imp.getName(), 'Alias')
        self.assertTrue(check(imp, 'ElementImport.imported_element_is_public'))
        target.visibility = Uml.VisibilityKind.private
        self.assertFalse(check(imp, 'ElementImport.imported_element_is_public'))
        target.visibility = None
        self.assertTrue(check(imp, 'ElementImport.imported_element_is_public'))
        for cls, rule in ((Uml.ElementImport, 'ElementImport.visibility_public_or_private'),
                          (Uml.PackageImport, 'PackageImport.public_or_private')):
            value = cls()
            for visibility, valid in ((Uml.VisibilityKind.public, True), (Uml.VisibilityKind.private, True),
                                      (Uml.VisibilityKind.protected, False), (None, False)):
                value.visibility = visibility
                self.assertEqual(check(value, rule), valid)

    @verifies('Namespace.getNamesOfMember', 'Namespace.importedMember', 'Namespace.importMembers', 'Namespace.excludeCollisions', 'Namespace-member', 'Namespace-ownedMember')
    def test_import_aliases_collision_exclusion_and_owned_member_collision(self):
        package = Uml.Package()
        a, b = Uml.Class(name='A'), Uml.Class(name='B')
        package.elementImport.extend([Uml.ElementImport(importedElement=a, alias='Shared'),
                                      Uml.ElementImport(importedElement=b, alias='Shared')])
        self.assertEqual(package.getNamesOfMember(a), ['Shared'])
        self.assertEqual(package.excludeCollisions([a, b]), [])
        self.assertEqual(package.importedMember, [])
        package.elementImport[1].alias = 'Other'
        self.assertEqual(package.excludeCollisions([a, b]), [a, b])
        self.assertEqual(package.importedMember, [a, b])
        package.packagedElement.append(Uml.Class(name='Other'))
        self.assertEqual(package.importMembers([a, b]), [a])
        self.assertEqual(list(package.ownedMember), list(package.packagedElement))
        self.assertIn(a, package.member)

    @verifies('NamedElement.isDistinguishableFrom', 'Namespace.membersAreDistinguishable', 'Namespace.members_distinguishable')
    def test_distinguishability_uses_kind_and_names(self):
        package = Uml.Package()
        a, b = Uml.Class(name='Same'), Uml.Class(name='Same')
        package.packagedElement.extend([a, b])
        self.assertFalse(a.isDistinguishableFrom(b, package))
        self.assertFalse(package.membersAreDistinguishable())
        self.assertFalse(check(package, 'Namespace.members_distinguishable'))
        b.name = 'Other'
        self.assertTrue(package.membersAreDistinguishable())
        package.packagedElement.append(Uml.Package(name='Same'))
        self.assertTrue(check(package, 'Namespace.members_distinguishable'))

    @verifies('Namespace.cannot_import_self', 'Namespace.cannot_import_ownedMembers')
    def test_namespace_cannot_import_itself_or_its_owned_members(self):
        package, member = Uml.Package(), Uml.Class()
        package.packagedElement.append(member)
        self.assertTrue(check(package, 'Namespace.cannot_import_self'))
        package.packageImport.append(Uml.PackageImport(importedPackage=package))
        self.assertFalse(check(package, 'Namespace.cannot_import_self'))
        self.assertTrue(check(package, 'Namespace.cannot_import_ownedMembers'))
        package.elementImport.append(Uml.ElementImport(importedElement=member))
        self.assertFalse(check(package, 'Namespace.cannot_import_ownedMembers'))

    @verifies('TemplateableElement.isTemplate', 'TemplateableElement.parameterableElements',
              'ParameterableElement.isTemplateParameter', 'NamedElement.allNamespaces', 'TemplateParameter-ownedParameteredElement')
    def test_template_owned_element_namespace_and_parameter_membership(self):
        package, template = Uml.Package(name='P'), Uml.Class(name='T')
        package.packagedElement.append(template)
        self.assertFalse(template.uml_operation('TemplateableElement', 'isTemplate'))
        formal_element = Uml.Class(name='F', visibility=None)
        parameter = Uml.ClassifierTemplateParameter(ownedParameteredElement=formal_element)
        signature = Uml.RedefinableTemplateSignature(ownedParameter=[parameter])
        template.ownedTemplateSignature = signature
        self.assertTrue(template.uml_operation('TemplateableElement', 'isTemplate'))
        self.assertTrue(formal_element.isTemplateParameter())
        self.assertIn(formal_element, template.parameterableElements())
        self.assertEqual(formal_element.allNamespaces(), [template, package])
        self.assertEqual(formal_element.qualifiedName, 'P::T::F')
        self.assertIs(parameter.parameteredElement, formal_element)
        parameter.ownedParameteredElement = None
        self.assertIsNone(formal_element.owner)
        self.assertTrue(formal_element.isTemplateParameter())  # Still the nonowned parameteredElement.
        parameter.parameteredElement = None
        self.assertFalse(formal_element.isTemplateParameter())
        with self.assertRaises(TypeError): parameter.ownedParameteredElement = Uml.Operation()
        self.assertIsNone(parameter.parameteredElement)

    @verifies('DirectedRelationship-source', 'DirectedRelationship-target', 'Relationship-relatedElement')
    def test_directed_relationship_derived_unions_follow_mutations(self):
        client, supplier = Uml.Class(), Uml.Class()
        dependency = Uml.Dependency(client=[client], supplier=[supplier])
        self.assertEqual(list(dependency.source), [client])
        self.assertEqual(list(dependency.target), [supplier])
        self.assertEqual(set(dependency.relatedElement), {client, supplier})
        dependency.client.clear()
        self.assertEqual(list(dependency.source), [])
        self.assertEqual(list(dependency.relatedElement), [supplier])

    @verifies('ParameterableElement.isCompatibleWith', 'TemplateParameter.must_be_compatible', 'TemplateParameterSubstitution.must_be_compatible')
    def test_template_default_and_actual_have_the_formal_metaclass_kind(self):
        parameter = Uml.TemplateParameter(parameteredElement=Uml.Class(), default=Uml.Component())
        self.assertTrue(parameter.default.isCompatibleWith(parameter.parameteredElement))
        self.assertTrue(check(parameter, 'TemplateParameter.must_be_compatible'))
        parameter.default = Uml.Operation()
        self.assertFalse(check(parameter, 'TemplateParameter.must_be_compatible'))
        substitution = Uml.TemplateParameterSubstitution(formal=parameter, actual=Uml.Class())
        self.assertTrue(check(substitution, 'TemplateParameterSubstitution.must_be_compatible'))
        substitution.actual = Uml.Operation()
        self.assertFalse(check(substitution, 'TemplateParameterSubstitution.must_be_compatible'))

    @verifies('TemplateBinding.parameter_substitution_formal', 'TemplateBinding.one_parameter_substitution')
    def test_binding_substitutions_reference_signature_parameters_once(self):
        p = Uml.TemplateParameter(parameteredElement=Uml.Class())
        signature = Uml.RedefinableTemplateSignature(ownedParameter=[p])
        first = Uml.TemplateParameterSubstitution(formal=p, actual=Uml.Class())
        binding = Uml.TemplateBinding(signature=signature, parameterSubstitution=[first])
        self.assertTrue(check(binding, 'TemplateBinding.parameter_substitution_formal'))
        self.assertTrue(check(binding, 'TemplateBinding.one_parameter_substitution'))
        second = Uml.TemplateParameterSubstitution(formal=p, actual=Uml.Class())
        binding.parameterSubstitution.append(second)
        self.assertFalse(check(binding, 'TemplateBinding.one_parameter_substitution'))
        second.formal = Uml.TemplateParameter(parameteredElement=Uml.Class())
        self.assertFalse(check(binding, 'TemplateBinding.parameter_substitution_formal'))

    @verifies('TemplateSignature.own_elements', 'TemplateSignature.unique_parameters')
    def test_signature_parameter_ownership_and_distinct_names(self):
        template = Uml.Class()
        a, b = Uml.Property(name='A'), Uml.Property(name='B')
        template.ownedAttribute.extend([a, b])
        p, q = Uml.TemplateParameter(parameteredElement=a), Uml.TemplateParameter(parameteredElement=b)
        signature = Uml.RedefinableTemplateSignature(ownedParameter=[p, q])
        template.ownedTemplateSignature = signature
        self.assertTrue(check(signature, 'TemplateSignature.own_elements'))
        self.assertTrue(check(signature, 'TemplateSignature.unique_parameters'))
        b.name = 'A'
        self.assertFalse(check(signature, 'TemplateSignature.unique_parameters'))
        template.ownedAttribute.remove(b)
        self.assertFalse(check(signature, 'TemplateSignature.own_elements'))

    @verifies('Constraint.not_apply_to_self', 'Constraint.boolean_value', 'Constraint.no_side_effects')
    def test_constraint_boolean_value_and_no_self_application(self):
        constraint = Uml.Constraint(specification=Uml.LiteralBoolean(value=False))
        self.assertTrue(check(constraint, 'Constraint.boolean_value'))
        self.assertTrue(check(constraint, 'Constraint.no_side_effects'))
        self.assertTrue(check(constraint, 'Constraint.not_apply_to_self'))
        constraint.constrainedElement.append(constraint)
        self.assertFalse(check(constraint, 'Constraint.not_apply_to_self'))
        constraint.specification = Uml.LiteralString(value='not boolean', type=Uml.PrimitiveType(name='Boolean'))
        self.assertFalse(check(constraint, 'Constraint.boolean_value'))

    @verifies('Constraint.no_side_effects')
    def test_foreign_constraint_purity_requires_analyzer_facts(self):
        expression = Uml.OpaqueExpression(type=Uml.PrimitiveType(name='Boolean'))
        constraint = Uml.Constraint(specification=expression)
        with self.assertRaises(NativeNotImplemented): check(constraint, 'Constraint.no_side_effects')
        register_expression_facts(expression, pure=False)
        self.assertFalse(check(constraint, 'Constraint.no_side_effects'))
        register_expression_facts(expression, pure=True)
        self.assertTrue(check(constraint, 'Constraint.no_side_effects'))

    @verifies('Type.conformsTo')
    def test_type_default_query_is_distinct_from_classifier_override(self):
        cls = Uml.Class()
        self.assertFalse(cls.uml_operation('Type', 'conformsTo', cls))
        self.assertTrue(cls.conformsTo(cls))
