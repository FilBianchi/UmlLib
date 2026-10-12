"""Run from outside the checkout after installing its distribution."""
import Uml
from umltools import OperationResultError, ModelSession, DeletedElementError
from umltools.native import instances
from umltools.native import check
from umltools.stereotypes import apply_profile, apply_stereotype
from umltools.interaction_mapping import bind_gate_endpoint, mark_extra_global, map_occurrence_gate
from importlib.metadata import version
from importlib.resources import files


model = Uml.Model(name='Installed', packagedElement=[Uml.Class(name='Customer')])
assert model.packagedElement[0].qualifiedName == 'Installed::Customer'
assert len(Uml._classes.__all__) == 255
assert files('umltools.data').joinpath('UML.xmi').is_file()
assert not any(category == 'constraint' for category, _ in model.validate(recursive=True))
parent, target = Uml.Class(), Uml.Class()
child = Uml.Class(generalization=[Uml.Generalization(general=parent)])
channel = Uml.Dependency(client=[parent], supplier=[target])
flow = Uml.InformationFlow(informationSource=[child], informationTarget=[target], realization=[channel])
assert check(flow, 'InformationFlow.must_conform')
formal = Uml.Class()
parameter = Uml.ClassifierTemplateParameter(ownedParameteredElement=formal)
assert formal.isTemplateParameter() and parameter.parameteredElement is formal
try:
    Uml.LiteralReal().realValue()
except OperationResultError:
    pass
else:
    raise AssertionError('Required operation result was not checked')
with ModelSession():
    survivor, deleted = Uml.Class(), Uml.Class(ownedAttribute=[Uml.Property()])
    user = Uml.Property(type=deleted)
    removed = deleted.delete()
    assert len(removed) == 2 and deleted.is_deleted and user.type is None
    assert deleted not in instances(survivor, 'Class')
    try:
        deleted.allParents()
    except DeletedElementError:
        pass
    else:
        raise AssertionError('A tombstone remained queryable')
assert Uml.LiteralUnlimitedNatural().unlimitedValue() == 0
with ModelSession():
    owner, declarations, collaboration = Uml.Class(), Uml.Class(), Uml.Collaboration()
    actual, formal_role = Uml.Property(), Uml.Property()
    owner.ownedAttribute.append(actual)
    declarations.ownedAttribute.append(formal_role)
    collaboration.collaborationRole.append(formal_role)
    use = Uml.CollaborationUse(type=collaboration, roleBinding=[Uml.Dependency(client=[actual], supplier=[formal_role])])
    assert check(use, 'CollaborationUse.client_elements')
    assert check(use, 'CollaborationUse.every_role')
assert check(Uml.OpaqueBehavior(), 'Behavior.feature_of_context_classifier')
assert check(Uml.TimeEvent(when=Uml.TimeExpression(expr=Uml.LiteralInteger(value=0))), 'TimeEvent.when_non_negative')
leaf = Uml.State(entry=Uml.OpaqueBehavior())
protocol = Uml.ProtocolStateMachine(region=[Uml.Region(subvertex=[Uml.State(region=[Uml.Region(subvertex=[leaf])])])])
assert not check(protocol, 'ProtocolStateMachine.entry_exit_do')
with ModelSession():
    feature = Uml.Property()
    classifier = Uml.Class(ownedAttribute=[feature])
    action = Uml.ReadStructuralFeatureAction(structuralFeature=feature)
    assert check(action, 'StructuralFeatureAction.one_featuring_classifier')
    producer = Uml.OpaqueAction(outputValue=[Uml.OutputPin()])
    computed = Uml.ActionInputPin(fromAction=producer)
    assert check(computed, 'ActionInputPin.no_control_or_object_flow')
    Uml.ControlFlow(source=producer, target=Uml.ActivityFinalNode())
    assert not check(computed, 'ActionInputPin.no_control_or_object_flow')
    source = Uml.CentralBufferNode(upperBound=Uml.LiteralUnlimitedNatural(value=4))
    target = Uml.CentralBufferNode(upperBound=Uml.LiteralUnlimitedNatural(value=3))
    flow = Uml.ObjectFlow(source=source, target=target, weight=Uml.LiteralInteger(value=4))
    assert not check(flow, 'ObjectFlow.same_upper_bounds')
    assert not check(flow, 'ObjectFlow.target')
with ModelSession():
    assert Uml.Gate(name='explicit').getOperand() is None
    line = Uml.Lifeline()
    send, receive = Uml.MessageOccurrenceSpecification(covered=line), Uml.MessageOccurrenceSpecification(covered=line)
    operand = Uml.InteractionOperand(fragment=[send])
    interaction = Uml.Interaction(lifeline=[line], fragment=[Uml.CombinedFragment(operand=[operand]), receive])
    assert check(Uml.Message(sendEvent=send, receiveEvent=receive), 'Message.sending_receiving_message_event')
    guard = Uml.InteractionConstraint(specification=Uml.LiteralBoolean(value=True))
    operand.guard = guard
    assert check(guard, 'InteractionConstraint.dynamic_variables')
    guard.maxint = Uml.OpaqueExpression(body=['limit'], language=['custom'])
    assert ('unsupported constraint', 'InteractionConstraint.maxint_positive') in guard.validate()
with ModelSession():
    part = Uml.Property(type=Uml.ExecutionEnvironment(), aggregation=Uml.AggregationKind.composite)
    node = Uml.Device(ownedAttribute=[part])
    assert check(node, 'Node.internal_structure')
    shared = Uml.Class()
    first = Uml.UseCase(subject=[shared, Uml.Class()])
    second = Uml.UseCase(subject=[shared, Uml.Class()])
    Uml.Association(ownedEnd=[Uml.Property(type=first), Uml.Property(type=second)])
    assert not check(first, 'UseCase.no_association_to_use_case')
    component = Uml.Component()
    artifact = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=component)])
    environment = Uml.ExecutionEnvironment(deployment=[Uml.Deployment(deployedArtifact=[artifact])])
    assert environment.deployedElement == [component]
from umltools.static_requirements import deployed_elements
with ModelSession():
    wrong = Uml.Class()
    artifact = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=wrong)])
    instance = Uml.InstanceSpecification(classifier=[artifact])
    configuration = Uml.DeploymentSpecification()
    target = Uml.ExecutionEnvironment(deployment=[Uml.Deployment(deployedArtifact=[instance], configuration=[configuration])])
    assert target.deployedElement == []
    assert deployed_elements(target) == [wrong]
    assert ('constraint', 'prose:DeploymentSpecification.configured_instance_elements') in configuration.validate()
    signature = Uml.Operation(ownedParameter=[Uml.Parameter(type=wrong, direction=Uml.ParameterDirectionKind.return_)])
    reply = Uml.Message(signature=signature, messageSort=Uml.MessageSort.reply, argument=[Uml.LiteralInteger(type=Uml.Class())])
    assert check(reply, 'Message.signature_is_operation_reply')
    assert ('constraint', 'prose:Message.reply_argument_types') in reply.validate()
with ModelSession():
    a, b = Uml.Class(), Uml.Class()
    observation = Uml.DurationObservation(event=[a, a, b], firstEvent=[True, True, False])
    assert list(observation.event) == [a, b]
    node = Uml.StructuredActivityNode()
    first, second = Uml.Activity(), Uml.Activity()
    node.activity = first
    node.inActivity = second
    assert node.activity is second and node.owner is second and node.inActivity is second
    assert not first.node and list(second.structuredNode) == [node]
    cache = second.node
    second.delete()
    try:
        repr(cache)
    except DeletedElementError:
        pass
    else:
        raise AssertionError('Cached collection repr accepted a tombstone owner')
foreign = Uml.Class()
with ModelSession():
    dependency = Uml.Dependency(client=[foreign])
assert ('cross session reference', 'Dependency-client') in dependency.validate()
from umltools.stereotypes import apply_profile, apply_stereotype, unapply_profile
from umltools.profile_values import ProfileObject, register_profile_constraint
from umltools.profile_filtering import is_metaclass_available, create_profiled_element
with ModelSession():
    metaclass=Uml.Class(name='Class')
    metamodel=Uml.Model(packagedElement=[metaclass])
    integer=Uml.PrimitiveType(name='Integer')
    stereotype=Uml.Stereotype(name='Tagged')
    profile=Uml.Profile(packagedElement=[integer,stereotype],
                        metaclassReference=[Uml.ElementImport(importedElement=metaclass)])
    base=Uml.Property(name='base_Class',type=metaclass)
    stereotype.ownedAttribute.append(base)
    extension=Uml.Extension(memberEnd=[base],ownedEnd=Uml.ExtensionEnd(type=stereotype,
                            aggregation=Uml.AggregationKind.composite,lowerValue=Uml.LiteralInteger(value=0)))
    profile.packagedElement.append(extension)
    count=Uml.Property(name='count',type=integer,defaultValue=Uml.LiteralInteger(value=2))
    payload=Uml.Class(name='Payload'); profile.packagedElement.append(payload)
    child=Uml.Property(name='child',type=payload,aggregation=Uml.AggregationKind.composite,
                       lowerValue=Uml.LiteralInteger(value=0))
    stereotype.ownedAttribute.extend([count,child])
    model=Uml.Model(packagedElement=[Uml.Class()])
    apply_profile(model,profile,is_strict=True)
    assert is_metaclass_available(model,'Component')
    assert not is_metaclass_available(model,'State')
    assert isinstance(create_profiled_element(model,'Class'),Uml.Class)
    value=ProfileObject(payload,model)
    application=apply_stereotype(model.packagedElement[0],stereotype,values={'child':value})
    assert application.get_value('count')==2
    application.set_value('count',3)
    constraint=Uml.Constraint(name='positive'); stereotype.ownedRule.append(constraint)
    register_profile_constraint(constraint,lambda app:app.get_value('count')>0)
    assert application.validate()==[]
    from umltools.xmi import loads,dumps
    from umltools.stereotypes import applications
    exchanged=loads(dumps(model))
    restored_model=next(root for root in exchanged.roots if root.__spec__.name=='Model' and root.profileApplication)
    restored_application=applications(restored_model.packagedElement[0])[0]
    assert restored_application.get_value('count')==3
    assert restored_application.get_value('child').classifier.name=='Payload'
    assert restored_model.profileApplication[0].isStrict
    assert any(category=='unsupported stereotype application' for category,_ in restored_application.validate())
    unapply_profile(model,profile)
    assert application.is_deleted and value.is_deleted
    assert not model.packagedElement[0].is_deleted
print('Installed UmlLib', version('UmlLib'))
