"""Use-case graph/subject rules and deployment derivation/association contracts."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check
from semantic_cases import verifies


class UseCaseDeploymentCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    def rules(self, obj, *names, expected=True):
        for name in names:
            with self.subTest(rule=name): self.assertEqual(check(obj, name), expected)

    @verifies('UseCase.allIncludedUseCases', 'UseCase.cannot_include_self', 'UseCase.must_have_name',
              'Actor.must_have_name', 'ExtensionPoint.must_have_name')
    def test_include_diamond_cycles_deletion_and_optional_names(self):
        a, b, c, d = [Uml.UseCase(name=n) for n in ('A','B','C','D')]
        a.include.extend([Uml.Include(addition=b), Uml.Include(addition=c)])
        b.include.append(Uml.Include(addition=d))
        c.include.append(Uml.Include(addition=d))
        self.assertEqual(set(a.allIncludedUseCases()), {b, c, d})
        self.assertEqual(len(a.allIncludedUseCases()), 3)
        self.rules(a, 'UseCase.cannot_include_self')
        cyclic = Uml.Include(addition=a)
        d.include.append(cyclic)
        self.assertIn(a, a.allIncludedUseCases())
        self.rules(a, 'UseCase.cannot_include_self', expected=False)
        cyclic.delete()
        self.rules(a, 'UseCase.cannot_include_self')
        b.include[0].delete()
        self.assertIn(d, a.allIncludedUseCases())
        c.include[0].delete()
        self.assertEqual(set(a.allIncludedUseCases()), {b,c})
        a.include.append(Uml.Include())
        with self.assertRaises(ValueError): a.allIncludedUseCases()
        for cls, rule in ((Uml.UseCase,'UseCase.must_have_name'), (Uml.Actor,'Actor.must_have_name'),
                          (Uml.ExtensionPoint,'ExtensionPoint.must_have_name')):
            obj = cls()
            self.rules(obj, rule, expected=False)
            obj.name = ''  # Present empty names satisfy the declared notEmpty test on optional String.
            self.rules(obj, rule)

    @verifies('Extend.extension_points')
    def test_extension_points_belong_to_extended_case_and_inverse_rebinding(self):
        base, extension = Uml.UseCase(), Uml.UseCase()
        point = Uml.ExtensionPoint(name='checkout')
        base.extensionPoint.append(point)
        relation = Uml.Extend(extendedCase=base, extensionLocation=[point])
        extension.extend.append(relation)
        self.assertIs(relation.extension, extension)
        self.assertIs(point.useCase, base)
        self.rules(relation, 'Extend.extension_points')
        foreign = Uml.ExtensionPoint(name='foreign')
        extension.extensionPoint.append(foreign)
        relation.extensionLocation.append(foreign)
        self.rules(relation, 'Extend.extension_points', expected=False)
        relation.extensionLocation.remove(foreign)
        base.extensionPoint.remove(point)
        extension.extensionPoint.append(point)
        self.rules(relation, 'Extend.extension_points', expected=False)
        relation.extendedCase = extension
        self.rules(relation, 'Extend.extension_points')
        point.delete()
        self.assertEqual(relation.extensionLocation, [])
        self.assertIn(('multiplicity', 'Extend-extensionLocation'), relation.validate())

    @verifies('Actor.associations', 'UseCase.binary_associations')
    def test_actor_association_end_types_binary_and_session_extent(self):
        actor, use = Uml.Actor(), Uml.UseCase()
        first, second = Uml.Property(type=actor), Uml.Property(type=use)
        association = Uml.Association(ownedEnd=[first, second])
        self.rules(actor, 'Actor.associations')
        self.rules(use, 'UseCase.binary_associations')
        for allowed in (Uml.Class(), Uml.Component()):
            second.type = allowed
            self.rules(actor, 'Actor.associations')
        for rejected in (Uml.Actor(), Uml.OpaqueBehavior(), Uml.Interface()):
            second.type = rejected
            self.rules(actor, 'Actor.associations', expected=False)
        second.type = use
        association.ownedEnd.append(Uml.Property(type=Uml.Class()))
        self.rules(actor, 'Actor.associations', expected=False)
        self.rules(use, 'UseCase.binary_associations', expected=False)
        association.delete()
        self.rules(actor, 'Actor.associations')
        self.rules(use, 'UseCase.binary_associations')
        with ModelSession():
            other = Uml.UseCase()
            Uml.Association(ownedEnd=[Uml.Property(type=other) for _ in range(3)])
        self.rules(use, 'UseCase.binary_associations')
        self.rules(other, 'UseCase.binary_associations', expected=False)

    @verifies('UseCase.no_association_to_use_case')
    def test_subject_intersections_not_subject_union_cardinality(self):
        shared, one, two = Uml.Class(), Uml.Class(), Uml.Class()
        a = Uml.UseCase(subject=[shared, one])
        b = Uml.UseCase(subject=[shared, two])
        association = Uml.Association(ownedEnd=[Uml.Property(type=a), Uml.Property(type=b)])
        self.rules(a, 'UseCase.no_association_to_use_case', expected=False)
        self.rules(b, 'UseCase.no_association_to_use_case', expected=False)
        b.subject.remove(shared)
        self.rules(a, 'UseCase.no_association_to_use_case')
        b.subject.clear()
        self.rules(a, 'UseCase.no_association_to_use_case')
        a.subject.clear()
        self.rules(a, 'UseCase.no_association_to_use_case')
        association.memberEnd[1].type = a
        self.rules(a, 'UseCase.no_association_to_use_case')  # The declared rule concerns distinct UseCases.

    @verifies('Node.internal_structure', 'CommunicationPath.association_ends')
    def test_node_parts_are_typed_by_nodes_and_path_targets(self):
        part = Uml.Property(type=Uml.ExecutionEnvironment(), aggregation=Uml.AggregationKind.composite)
        node = Uml.Device(ownedAttribute=[part])
        self.rules(node, 'Node.internal_structure')
        part.type = Uml.Device()
        self.rules(node, 'Node.internal_structure')
        part.type = Uml.Component()
        self.rules(node, 'Node.internal_structure', expected=False)
        part.type = None
        self.rules(node, 'Node.internal_structure', expected=False)
        part.aggregation = Uml.AggregationKind.none
        self.rules(node, 'Node.internal_structure')
        ends = [Uml.Property(type=node), Uml.Property(type=Uml.ExecutionEnvironment())]
        path = Uml.CommunicationPath(ownedEnd=ends)
        self.rules(path, 'CommunicationPath.association_ends')
        ends[1].type = Uml.Component()
        self.rules(path, 'CommunicationPath.association_ends', expected=False)

    @verifies('DeploymentTarget.deployedElement', 'DeploymentTarget-deployedElement',
              'DeploymentSpecification.deployment_target', 'DeploymentSpecification.deployed_elements')
    def test_manifestations_deployed_elements_configuration_and_cleanup(self):
        component, another = Uml.Component(), Uml.Component()
        manifests = [Uml.Manifestation(utilizedElement=component), Uml.Manifestation(utilizedElement=component),
                     Uml.Manifestation(utilizedElement=another)]
        artifact = Uml.Artifact(manifestation=manifests)
        configuration = Uml.DeploymentSpecification()
        deployment = Uml.Deployment(deployedArtifact=[artifact], configuration=[configuration])
        target = Uml.ExecutionEnvironment(deployment=[deployment])
        self.assertIs(configuration.deployment, deployment)
        self.assertIs(deployment.location, target)
        self.assertEqual(set(target.deployedElement), {component, another})
        self.assertEqual(len(target.deployedElement), 2)
        self.rules(configuration, 'DeploymentSpecification.deployment_target', 'DeploymentSpecification.deployed_elements')
        manifests[2].utilizedElement = Uml.Class()
        self.rules(configuration, 'DeploymentSpecification.deployed_elements', expected=False)
        manifests[2].delete()
        self.rules(configuration, 'DeploymentSpecification.deployed_elements')
        target.deployment.remove(deployment)
        device = Uml.Device(deployment=[deployment])
        self.rules(configuration, 'DeploymentSpecification.deployment_target', expected=False)
        artifact.delete()
        self.assertEqual(device.deployedElement, [])
        self.assertEqual(deployment.deployedArtifact, [])
        self.assertIn(('multiplicity', 'Dependency-supplier'), deployment.validate())

    @verifies('DeploymentTarget.deployedElement', 'DeploymentTarget-deployedElement',
              'DeploymentSpecification.deployed_elements')
    def test_deployment_derivation_preserves_source_artifact_only_filter(self):
        component = Uml.Component()
        artifact = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=component)])
        instance = Uml.InstanceSpecification(classifier=[artifact])
        config = Uml.DeploymentSpecification()
        target = Uml.ExecutionEnvironment(deployment=[Uml.Deployment(deployedArtifact=[instance], configuration=[config])])
        # The XMI selects Artifact objects only, not instances classified by artifacts.
        self.assertEqual(target.deployedElement, [])
        self.rules(config, 'DeploymentSpecification.deployed_elements')
