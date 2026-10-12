"""Association, collaboration, component and port boundary examples."""
import unittest
import Uml
from umltools import ModelSession, OperationResultError
from umltools.native import check, NativeNotImplemented
from semantic_cases import verifies


def bounded(cls, lower=1, upper=1, **kwargs):
    return cls(lowerValue=Uml.LiteralInteger(value=lower), upperValue=Uml.LiteralUnlimitedNatural(value=upper), **kwargs)


class StructuredCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    @verifies('Association.endType', 'Association.specialized_end_number', 'Association.specialized_end_types',
              'Association.binary_associations', 'Association.association_ends', 'Association.ends_must_be_typed')
    def test_ordered_association_specialization_arity_types_and_aggregation(self):
        base, subtype, other = Uml.Class(), Uml.Class(), Uml.Class()
        subtype.generalization.append(Uml.Generalization(general=base))
        parent = Uml.Association(ownedEnd=[Uml.Property(type=base), Uml.Property(type=other)])
        child = Uml.Association(ownedEnd=[Uml.Property(type=subtype), Uml.Property(type=other)], generalization=[Uml.Generalization(general=parent)])
        self.assertEqual(list(child.endType), [subtype, other])
        self.assertTrue(check(child, 'Association.specialized_end_number'))
        self.assertTrue(check(child, 'Association.specialized_end_types'))
        child.memberEnd.reverse()
        self.assertFalse(check(child, 'Association.specialized_end_types'))
        child.memberEnd.reverse()
        child.ownedEnd.append(Uml.Property(type=base))
        self.assertFalse(check(child, 'Association.specialized_end_number'))
        self.assertTrue(check(child, 'Association.association_ends'))
        child.memberEnd[0].aggregation = Uml.AggregationKind.composite
        self.assertFalse(check(child, 'Association.binary_associations'))
        external = Uml.Property(type=other)
        owner = Uml.Class(ownedAttribute=[external])
        child.memberEnd.append(external)
        self.assertFalse(check(child, 'Association.association_ends'))
        external.type = None
        self.assertFalse(check(child, 'Association.ends_must_be_typed'))
        with self.assertRaises(OperationResultError): _ = child.endType
        reflexive = Uml.Association(ownedEnd=[Uml.Property(type=base), Uml.Property(type=base)])
        self.assertEqual(list(reflexive.endType), [base])
        reflexive.memberEnd[0].aggregation = Uml.AggregationKind.composite
        self.assertTrue(check(reflexive, 'Association.binary_associations'))
        reflexive.memberEnd[1].aggregation = Uml.AggregationKind.shared
        self.assertFalse(check(reflexive, 'Association.binary_associations'))

    @verifies('AssociationClass.cannot_be_defined', 'AssociationClass.disjoint_attributes_ends')
    def test_association_class_end_types_and_composite_attribute_end_exclusivity(self):
        type_ = Uml.Class()
        association = Uml.AssociationClass(ownedEnd=[Uml.Property(type=type_), Uml.Property(type=type_)])
        self.assertTrue(check(association, 'AssociationClass.cannot_be_defined'))
        self.assertTrue(check(association, 'AssociationClass.disjoint_attributes_ends'))
        end = association.ownedEnd[0]
        with self.assertRaises(ValueError): association.ownedAttribute.append(end)
        self.assertEqual(list(association.ownedAttribute), [])
        end.type = association
        self.assertFalse(check(association, 'AssociationClass.cannot_be_defined'))
        descendant = Uml.Class(generalization=[Uml.Generalization(general=association)])
        end.type = descendant
        self.assertFalse(check(association, 'AssociationClass.cannot_be_defined'))

    @verifies('Class.passive_class', 'Class.superClass', 'Class.extension')
    def test_passive_class_superclasses_and_extension_on_a_subtype(self):
        base, child = Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        self.assertEqual(list(child.superClass), [base])
        self.assertTrue(check(child, 'Class.passive_class'))
        child.ownedReception.append(Uml.Reception(signal=Uml.Signal()))
        self.assertFalse(check(child, 'Class.passive_class'))
        child.isActive = True
        self.assertTrue(check(child, 'Class.passive_class'))
        stereotype = Uml.Stereotype()
        base_link = Uml.Property(type=child)
        stereotype.ownedAttribute.append(base_link)
        extension = Uml.Extension(ownedEnd=Uml.ExtensionEnd(type=stereotype), memberEnd=[base_link])
        self.assertEqual(list(base.extension), [extension])
        self.assertEqual(list(child.extension), [extension])
        base_link.type = base
        self.assertEqual(list(child.extension), [])

    @verifies('StructuredClassifier.part', 'StructuredClassifier.allRoles', 'EncapsulatedClassifier.ownedPort', 'StructuredClassifier-role')
    def test_parts_ports_and_inherited_roles_recompute_after_edits(self):
        base, child = Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        inherited, own, part, port = Uml.Property(), Uml.Property(), Uml.Property(aggregation=Uml.AggregationKind.composite), Uml.Port()
        base.ownedAttribute.append(inherited)
        child.ownedAttribute.extend([own, part, port])
        self.assertEqual(set(child.allRoles()), {inherited, own, part, port})
        self.assertEqual(set(child.role), {own, part, port})
        self.assertIn(part, child.part)
        self.assertNotIn(own, child.part)
        self.assertEqual(list(child.ownedPort), [port])
        part.aggregation = Uml.AggregationKind.none
        self.assertNotIn(part, child.part)
        child.ownedAttribute.remove(port)
        self.assertEqual(list(child.ownedPort), [])

    @verifies('Component.provided', 'Component.required', 'Component.no_nested_classifiers', 'Component.no_packaged_elements')
    def test_component_interfaces_union_realizers_parents_and_conjugated_ports(self):
        provided, required, port_interface = Uml.Interface(), Uml.Interface(), Uml.Interface()
        parent, component = Uml.Component(), Uml.Component()
        component.generalization.append(Uml.Generalization(general=parent))
        realizer = Uml.Class()
        Uml.Realization(client=[realizer], supplier=[provided])
        Uml.Usage(client=[realizer], supplier=[required])
        realization = Uml.ComponentRealization(abstraction=parent, realizingClassifier=[realizer])
        port = Uml.Port(type=port_interface, isConjugated=True)
        parent.ownedAttribute.append(port)
        self.assertEqual(set(component.provided), {provided})
        self.assertEqual(set(component.required), {required, port_interface})
        self.assertIn(realization, parent.realization)
        realization.realizingClassifier.clear()
        self.assertEqual(list(component.provided), [])
        component.nestedClassifier.append(Uml.Class())
        self.assertFalse(check(component, 'Component.no_nested_classifiers'))
        top_level = Uml.Component(packagedElement=[Uml.Class()])
        self.assertTrue(check(top_level, 'Component.no_packaged_elements'))
        container = Uml.Class(nestedClassifier=[top_level])
        self.assertFalse(check(top_level, 'Component.no_packaged_elements'))

    @verifies('Port.basicProvided', 'Port.basicRequired', 'Port.provided', 'Port.required', 'Port.port_aggregation',
              'Port.default_value', 'Port.encapsulated_owner')
    def test_port_type_interfaces_conjugation_default_values_and_owner(self):
        provided, required, type_ = Uml.Interface(), Uml.Interface(), Uml.Class()
        Uml.Realization(client=[type_], supplier=[provided])
        Uml.Usage(client=[type_], supplier=[required])
        port = Uml.Port(type=type_, aggregation=Uml.AggregationKind.composite)
        owner = Uml.Class(ownedAttribute=[port])
        self.assertEqual(port.basicProvided(), [provided])
        self.assertEqual(port.basicRequired(), [required])
        self.assertEqual(list(port.provided), [provided])
        self.assertEqual(list(port.required), [required])
        port.isConjugated = True
        self.assertEqual(list(port.provided), [required])
        self.assertEqual(list(port.required), [provided])
        self.assertTrue(check(port, 'Port.port_aggregation'))
        port.aggregation = Uml.AggregationKind.none
        self.assertFalse(check(port, 'Port.port_aggregation'))
        port.type = provided
        port.defaultValue = Uml.LiteralNull()
        self.assertFalse(check(port, 'Port.default_value'))
        port.defaultValue = None
        self.assertTrue(check(port, 'Port.default_value'))
        self.assertTrue(check(port, 'Port.encapsulated_owner'))
        owner.ownedAttribute.remove(port)
        self.assertFalse(check(port, 'Port.encapsulated_owner'))
        with self.assertRaises(ValueError): Uml.Port().basicProvided()

    @verifies('ConnectableElement.end', 'ConnectorEnd.definingEnd', 'ConnectorEnd.multiplicity', 'Connector.types')
    def test_connector_end_order_types_multiplicity_and_missing_association(self):
        first, second = Uml.Class(), Uml.Class()
        a, b = bounded(Uml.Property, 0, 4, type=first), bounded(Uml.Property, type=second)
        association = Uml.Association(ownedEnd=[a, b])
        role_a, role_b = Uml.Property(type=first), Uml.Property(type=second)
        ea, eb = bounded(Uml.ConnectorEnd, 1, 3, role=role_a), bounded(Uml.ConnectorEnd, role=role_b)
        connector = Uml.Connector(type=association, end=[ea, eb])
        self.assertEqual(list(role_a.end), [ea])
        self.assertIs(ea.definingEnd, a)
        self.assertIs(eb.definingEnd, b)
        self.assertTrue(check(connector, 'Connector.types'))
        self.assertTrue(check(ea, 'ConnectorEnd.multiplicity'))
        ea.upperValue.value = 5
        self.assertFalse(check(ea, 'ConnectorEnd.multiplicity'))
        connector.end.reverse()
        self.assertIs(ea.definingEnd, b)
        self.assertFalse(check(connector, 'Connector.types'))
        connector.type = None
        self.assertIsNone(ea.definingEnd)
        self.assertTrue(check(ea, 'ConnectorEnd.multiplicity'))
        ea.delete()
        self.assertEqual(list(role_a.end), [])

    @verifies('Connector.kind', 'Connector.roles', 'ConnectorEnd.role_and_part_with_port',
              'ConnectorEnd.part_with_port_empty', 'ConnectorEnd.self_part_with_port')
    def test_delegation_behavior_ports_parts_and_valid_role_contexts(self):
        interface, owner, part_type = Uml.Interface(), Uml.Class(), Uml.Class()
        boundary, internal = Uml.Port(type=interface), Uml.Port(type=interface)
        part = Uml.Property(type=part_type, aggregation=Uml.AggregationKind.composite)
        owner.ownedAttribute.extend([boundary, part])
        part_type.ownedAttribute.append(internal)
        direct, through = Uml.ConnectorEnd(role=boundary), Uml.ConnectorEnd(role=internal, partWithPort=part)
        connector = Uml.Connector(end=[direct, through])
        owner.ownedConnector.append(connector)
        self.assertEqual(connector.kind, Uml.ConnectorKind.delegation)
        self.assertTrue(check(connector, 'Connector.roles'))
        self.assertTrue(check(through, 'ConnectorEnd.role_and_part_with_port'))
        self.assertTrue(check(direct, 'ConnectorEnd.part_with_port_empty'))
        boundary.isBehavior = True
        self.assertEqual(connector.kind, Uml.ConnectorKind.assembly)
        direct.partWithPort = part
        self.assertFalse(check(direct, 'ConnectorEnd.part_with_port_empty'))
        through.partWithPort = boundary
        self.assertFalse(check(through, 'ConnectorEnd.self_part_with_port'))
        through.partWithPort = part
        through.role = Uml.Property(type=interface)
        self.assertFalse(check(through, 'ConnectorEnd.role_and_part_with_port'))
        self.assertFalse(check(connector, 'Connector.roles'))

    @verifies('CollaborationUse.client_elements', 'CollaborationUse.every_role')
    def test_role_binding_context_uses_membership_not_physical_owner(self):
        context, declaration_owner, collaboration = Uml.Class(), Uml.Class(), Uml.Collaboration()
        client, first, second = Uml.Property(), Uml.Property(), Uml.Property()
        context.ownedAttribute.append(client)
        declaration_owner.ownedAttribute.extend([first, second])
        collaboration.collaborationRole.extend([first, second])
        binding = Uml.Dependency(client=[client], supplier=[first, second])
        use = Uml.CollaborationUse(type=collaboration, roleBinding=[binding])
        self.assertTrue(check(Uml.CollaborationUse(type=collaboration), 'CollaborationUse.client_elements'))
        self.assertTrue(check(use, 'CollaborationUse.client_elements'))
        self.assertTrue(check(use, 'CollaborationUse.every_role'))
        binding.supplier.remove(second)
        self.assertFalse(check(use, 'CollaborationUse.every_role'))
        extra = Uml.Collaboration(collaborationRole=[first])
        binding.supplier.append(second)
        self.assertFalse(check(use, 'CollaborationUse.client_elements'))  # Opposite association sets now differ.

    @verifies('CollaborationUse.connectors')
    def test_binding_context_can_be_a_classifier_using_inherited_role_declarations(self):
        declaration, context, formal = Uml.Class(), Uml.Class(), Uml.Collaboration()
        context.generalization.append(Uml.Generalization(general=declaration))
        actual_a, actual_b, formal_a, formal_b = [Uml.Property(name=str(i)) for i in range(4)]
        declaration.ownedAttribute.extend([actual_a, actual_b])
        formal.ownedAttribute.extend([formal_a, formal_b])
        formal.collaborationRole.extend([formal_a, formal_b])
        formal.ownedConnector.append(Uml.Connector(end=[Uml.ConnectorEnd(role=formal_a), Uml.ConnectorEnd(role=formal_b)]))
        context.ownedConnector.append(Uml.Connector(end=[Uml.ConnectorEnd(role=actual_a), Uml.ConnectorEnd(role=actual_b)]))
        use = Uml.CollaborationUse(type=formal, roleBinding=[Uml.Dependency(client=[actual_a], supplier=[formal_a]), Uml.Dependency(client=[actual_b], supplier=[formal_b])])
        context.collaborationUse.append(use)
        self.assertTrue(check(use, 'CollaborationUse.client_elements'))
        self.assertTrue(check(use, 'CollaborationUse.connectors'))
        self.assertTrue(check(context.ownedConnector[0], 'Connector.roles'))
        alternate = Uml.Collaboration(collaborationRole=[actual_a, actual_b])
        context.collaborationUse.remove(use)
        with self.assertRaises(NativeNotImplemented): check(use, 'CollaborationUse.connectors')

    @verifies('CollaborationUse.connectors')
    def test_collaboration_connectors_correspond_by_binding_and_type_conformance(self):
        collaboration, context = Uml.Collaboration(), Uml.Class()
        formal_a, formal_b, actual_a, actual_b = [Uml.Property() for _ in range(4)]
        collaboration.ownedAttribute.extend([formal_a, formal_b])
        collaboration.collaborationRole.extend([formal_a, formal_b])
        context.ownedAttribute.extend([actual_a, actual_b])
        specification = Uml.Connector(end=[Uml.ConnectorEnd(role=formal_a), Uml.ConnectorEnd(role=formal_b)])
        correspondence = Uml.Connector(end=[Uml.ConnectorEnd(role=actual_a), Uml.ConnectorEnd(role=actual_b)])
        collaboration.ownedConnector.append(specification)
        context.ownedConnector.append(correspondence)
        use = Uml.CollaborationUse(type=collaboration, roleBinding=[Uml.Dependency(client=[actual_a], supplier=[formal_a]), Uml.Dependency(client=[actual_b], supplier=[formal_b])])
        self.assertTrue(check(use, 'CollaborationUse.connectors'))
        base_type = Uml.Association(ownedEnd=[Uml.Property(type=Uml.Class()), Uml.Property(type=Uml.Class())])
        specialized = Uml.Association(ownedEnd=[Uml.Property(type=base_type.memberEnd[0].type), Uml.Property(type=base_type.memberEnd[1].type)], generalization=[Uml.Generalization(general=base_type)])
        specification.type, correspondence.type = specialized, base_type
        self.assertTrue(check(use, 'CollaborationUse.connectors'))
        correspondence.type = Uml.Association()
        self.assertFalse(check(use, 'CollaborationUse.connectors'))
        correspondence.type = None
        correspondence.end[1].role = Uml.Property()
        self.assertFalse(check(use, 'CollaborationUse.connectors'))
