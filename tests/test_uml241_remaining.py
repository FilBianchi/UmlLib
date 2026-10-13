"""Counterexamples and independent graph scenarios for every remaining 2.4.1 family."""
import unittest
import Uml241 as U
import Uml251 as V
from Uml241.native import check,NativeNotImplemented
from Uml241.semantic_facts import register_semantic_facts


class Remaining241Cases(unittest.TestCase):
    def setUp(self):
        self.session=U.ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)

    def test_region_state_machine_extensions_preserve_inherited_structure(self):
        original=U.Region(subvertex=[U.State(name='Existing')])
        self.assertFalse(original.isConsistentWith(U.Region()))
        extension=U.Region(extendedRegion=original,subvertex=[U.State(name='Added')])
        self.assertTrue(original.isConsistentWith(extension))
        extension.subvertex[0].redefinedState=U.State()
        self.assertFalse(original.isConsistentWith(extension))
        extension.subvertex[0].redefinedState=original.subvertex[0]
        self.assertTrue(original.isConsistentWith(extension))
        transitive=U.Region(extendedRegion=extension,subvertex=[U.State(redefinedState=original.subvertex[0])])
        self.assertTrue(extension.isConsistentWith(transitive))
        state=U.State(region=[original])
        self.assertFalse(state.isConsistentWith(U.State()))
        self.assertTrue(state.isConsistentWith(U.State(region=[extension])))
        machine=U.StateMachines.StateMachine(region=[U.Region()])
        self.assertFalse(machine.isConsistentWith(U.StateMachines.StateMachine()))
        self.assertTrue(machine.isConsistentWith(U.StateMachines.StateMachine(extendedStateMachine=[machine])))

    def test_transformation_purity_is_explicit_and_trigger_assignment_is_conditional(self):
        type_=U.Class()
        behavior=U.OpaqueBehavior(ownedParameter=[U.Parameter(type=type_),U.Parameter(type=type_,direction=U.ParameterDirectionKind.return_)])
        flow=U.ObjectFlow(source=U.CentralBufferNode(type=type_),target=U.CentralBufferNode(type=type_),transformation=behavior)
        with self.assertRaises(NativeNotImplemented):check(flow,'ObjectFlow.transformation_behaviour')
        register_semantic_facts(behavior,pure=True)
        with self.assertRaises(TypeError):register_semantic_facts(behavior,pure=1)
        with self.assertRaises(TypeError):register_semantic_facts(V.OpaqueBehavior(),pure=True)
        with self.assertRaises(ValueError):register_semantic_facts(behavior,unknown=True)
        self.assertTrue(check(flow,'ObjectFlow.transformation_behaviour'))
        register_semantic_facts(behavior,pure=False)
        self.assertFalse(check(flow,'ObjectFlow.transformation_behaviour'))
        operation=U.Operation(ownedParameter=[U.Parameter(type=type_)])
        other=U.Operation(ownedParameter=[U.Parameter(type=U.Class())])
        transition=U.Transition(trigger=[U.Trigger(event=U.CallEvent(operation=operation)),U.Trigger(event=U.CallEvent(operation=other))])
        with self.assertRaises(NativeNotImplemented):check(transition,'Transition.signatures_compatible')
        register_semantic_facts(transition,trigger_parameters_assigned=False)
        self.assertTrue(check(transition,'Transition.signatures_compatible'))
        register_semantic_facts(transition,trigger_parameters_assigned=True)
        self.assertFalse(check(transition,'Transition.signatures_compatible'))

    def test_inheritance_overrides_and_visibility(self):
        original=U.Property(name='value',type=U.PrimitiveType(name='Integer'))
        parent=U.Class(ownedAttribute=[original])
        replacement=U.Property(name='value',type=original.type,redefinedProperty=[original])
        child=U.Class(generalization=[U.Generalization(general=parent)],ownedAttribute=[replacement])
        self.assertEqual(child.allParents(),[parent]);self.assertTrue(child.conformsTo(parent))
        self.assertEqual(child.inheritedMember,[])
        self.assertEqual(child.uml_operation('Classifier','inherit',[original]),[original])
        self.assertEqual(child.inherit([original]),[])
        self.assertEqual(original.featuringClassifier,[parent])
        original.visibility=U.VisibilityKind.private
        self.assertFalse(child.hasVisibilityOf(original))
        original.visibility=U.VisibilityKind.public
        self.assertTrue(child.hasVisibilityOf(original))

    def test_property_signatures_defaults_and_owned_opposites(self):
        type_=U.Class();p=U.Property(type=type_,defaultValue=U.LiteralInteger(value=42))
        owner=U.Class(ownedAttribute=[p])
        self.assertTrue(p.isAttribute(p));self.assertEqual(p.default,'42')
        with self.assertRaises(TypeError):p.isAttribute()
        first,second=U.Property(type=type_),U.Property(type=type_)
        association=U.Association(ownedEnd=[first,second])
        self.assertIsNone(first.opposite)
        self.assertTrue(check(association,'Association.binary_associations'))
        first.aggregation=U.AggregationKind.composite;second.aggregation=U.AggregationKind.composite
        self.assertTrue(check(association,'Association.binary_associations'))
        from Uml251.native import check as check25
        modern=V.Association(ownedEnd=[V.Property(aggregation=V.AggregationKind.composite),V.Property(aggregation=V.AggregationKind.composite)])
        self.assertFalse(check25(modern,'Association.binary_associations'))

    def test_operation_covariance_and_old_distinguishability(self):
        base_type=U.Class();specific=U.Class(generalization=[U.Generalization(general=base_type)])
        original=U.Operation(name='f',ownedParameter=[U.Parameter(type=base_type)])
        parent=U.Class(ownedOperation=[original])
        replacement=U.Operation(name='f',ownedParameter=[U.Parameter(type=specific)],redefinedOperation=[original])
        child=U.Class(generalization=[U.Generalization(general=parent)],ownedOperation=[replacement])
        self.assertTrue(original.isConsistentWith(replacement))
        self.assertTrue(original.isDistinguishableFrom(replacement,child))
        replacement.ownedParameter[0].type=base_type
        replacement.ownedParameter[0].name='different'
        peer=U.Operation(name='f',ownedParameter=[U.Parameter(type=base_type,name='another')])
        parent.ownedOperation.append(peer)
        self.assertFalse(original.isDistinguishableFrom(peer,parent))

    def test_connectors_ports_interfaces_and_destruction(self):
        interface=U.Interface(ownedOperation=[U.Operation(name='send')])
        provider_type=U.Class(interfaceRealization=[U.InterfaceRealization(contract=interface)])
        consumer_type=U.Class();U.Usage(client=[consumer_type],supplier=[interface])
        consumer,provider=U.Port(type=consumer_type),U.Port(type=provider_type)
        connector=U.Connector(end=[U.ConnectorEnd(role=consumer),U.ConnectorEnd(role=provider)])
        owner=U.Class(ownedAttribute=[consumer,provider],ownedConnector=[connector])
        consumer.isBehavior=True;provider.isBehavior=True
        self.assertEqual(provider.provided,[interface]);self.assertEqual(consumer.required,[interface])
        self.assertTrue(check(connector,'Connector.between_interfaces_ports'))
        self.assertTrue(check(connector,'Connector.roles'))
        with self.assertRaises(NativeNotImplemented):check(provider,'Port.port_destroyed')
        removed=provider.delete()
        self.assertIn(connector,removed);self.assertTrue(connector.is_deleted)
        self.assertFalse(consumer.is_deleted)

    def test_component_realizing_interfaces_and_nested_defaults(self):
        interface=U.Interface();realizer=U.Class(interfaceRealization=[U.InterfaceRealization(contract=interface)])
        component=U.Component(realization=[U.ComponentRealization(realizingClassifier=[realizer])])
        self.assertEqual(component.realizedInterfaces(realizer),[interface])
        self.assertEqual(component.provided,[interface])
        self.assertTrue(U.Parameter(defaultValue=U.LiteralBoolean(value=True)).default=='true')
        literal=U.EnumerationLiteral();enum=U.Enumeration(ownedLiteral=[literal])
        self.assertTrue(check(literal,'EnumerationLiteral.classifier_equals_owning_enumeration'))

    def test_behavior_context_method_uniqueness_and_function_datatypes(self):
        operation=U.Operation();first,second=U.OpaqueBehavior(specification=operation),U.OpaqueBehavior(specification=operation)
        owner=U.Class(ownedOperation=[operation],ownedBehavior=[first,second])
        self.assertIs(first.context,owner)
        self.assertFalse(check(first,'Behavior.most_one_behaviour'))
        owner.ownedBehavior.remove(second)
        self.assertTrue(check(first,'Behavior.most_one_behaviour'))
        integer=U.PrimitiveType(name='Integer')
        function=U.FunctionBehavior(ownedParameter=[U.Parameter(type=integer,direction=U.ParameterDirectionKind.return_)])
        self.assertTrue(check(function,'FunctionBehavior.types_of_parameters'))
        self.assertTrue(check(function,'FunctionBehavior.one_output_parameter'))

    def test_state_ancestors_context_and_lca_are_old_version_contracts(self):
        leaf=U.State();parent=U.State(region=[U.Region(subvertex=[leaf])]);peer=U.State()
        owner=U.Class();machine=U.StateMachines.StateMachine(region=[U.Region(subvertex=[parent,peer])])
        owner.ownedBehavior.append(machine)
        self.assertTrue(machine.ancestor(parent,leaf));self.assertFalse(machine.ancestor(leaf,parent))
        self.assertIs(machine.LCA(leaf,parent),parent)
        self.assertIs(machine.LCA(parent,peer),machine)
        self.assertIs(leaf.redefinitionContext,owner)
        machine.generalization.append(U.Generalization(general=U.StateMachines.StateMachine()))
        self.assertIs(leaf.redefinitionContext,machine)

    def test_state_transitions_and_protocol_history(self):
        start,end=U.State(),U.FinalState()
        transition=U.Transition(source=start,target=end)
        region=U.Region(subvertex=[start,end],transition=[transition])
        machine=U.StateMachines.StateMachine(region=[region])
        self.assertEqual(start.outgoing,[transition]);self.assertEqual(end.incoming,[transition])
        self.assertTrue(check(end,'FinalState.no_outgoing_transitions'))
        end.outgoing # Derivation is read-only, not a writable inverse slot.
        transition.source=end
        self.assertFalse(check(end,'FinalState.no_outgoing_transitions'))
        protocol=U.ProtocolStateMachine(region=[U.Region(subvertex=[U.Pseudostate(kind=U.PseudostateKind.deepHistory)])])
        self.assertFalse(check(protocol,'ProtocolStateMachine.deep_or_shallow_history'))

    def test_missing_execution_facts_do_not_succeed(self):
        activity=U.Activity();owner=U.Class(ownedBehavior=[activity])
        with self.assertRaises(NativeNotImplemented):check(activity,'Activity.autonomous')
        register_semantic_facts(activity,autonomous=True)
        self.assertFalse(check(activity,'Activity.autonomous'))
        register_semantic_facts(activity,autonomous=False)
        self.assertTrue(check(activity,'Activity.autonomous'))
        event=U.TimeEvent(isRelative=True)
        with self.assertRaises(NativeNotImplemented):check(event,'TimeEvent.starting_time')
        register_semantic_facts(event,starting_time_available=False)
        self.assertFalse(check(event,'TimeEvent.starting_time'))
        register_semantic_facts(event,starting_time_available=True)
        self.assertTrue(check(event,'TimeEvent.starting_time'))

    def test_activity_parameter_nodes_are_at_most_not_exactly_two(self):
        parameter=U.Parameter(direction=U.ParameterDirectionKind.inout)
        node=U.ActivityParameterNode(parameter=parameter)
        activity=U.Activity(ownedParameter=[parameter],node=[node])
        self.assertTrue(check(node,'ActivityParameterNode.maximum_two_parameter_nodes'))
        self.assertTrue(check(activity,'Activity.activity_parameter_node'))
        node2,node3=U.ActivityParameterNode(parameter=parameter),U.ActivityParameterNode(parameter=parameter)
        activity.node.extend([node2,node3])
        self.assertFalse(check(node,'ActivityParameterNode.maximum_two_parameter_nodes'))

    def test_call_pins_require_old_exact_type_and_multiplicity(self):
        parent=U.Class();specific=U.Class(generalization=[U.Generalization(general=parent)])
        behavior=U.OpaqueBehavior(ownedParameter=[U.Parameter(type=parent)])
        call=U.CallBehaviorAction(behavior=behavior,argument=[U.InputPin(type=specific)])
        self.assertFalse(check(call,'CallBehaviorAction.type_ordering_multiplicity'))
        call.argument[0].type=parent
        self.assertTrue(check(call,'CallBehaviorAction.type_ordering_multiplicity'))
        call.argument[0].upperValue=U.LiteralUnlimitedNatural(value=2)
        self.assertFalse(check(call,'CallBehaviorAction.type_ordering_multiplicity'))

    def test_insert_position_and_unmarshall_contracts(self):
        integer=U.PrimitiveType(name='Integer');natural=U.PrimitiveType(name='UnlimitedNatural')
        feature=U.Property(type=integer,isOrdered=True);owner=U.Class(ownedAttribute=[feature])
        insert=U.AddStructuralFeatureValueAction(structuralFeature=feature)
        self.assertFalse(check(insert,'AddStructuralFeatureValueAction.unlimited_natural_and_multiplicity'))
        insert.insertAt=U.InputPin(type=natural)
        self.assertTrue(check(insert,'AddStructuralFeatureValueAction.unlimited_natural_and_multiplicity'))
        action=U.UnmarshallAction(unmarshallType=owner,object=U.InputPin(type=owner),result=[U.OutputPin(type=integer,isOrdered=True)])
        self.assertTrue(check(action,'UnmarshallAction.unmarshallType_is_classifier'))
        self.assertTrue(check(action,'UnmarshallAction.type_and_ordering'))
        action.result[0].type=natural
        self.assertFalse(check(action,'UnmarshallAction.type_and_ordering'))

    def test_activity_edges_groups_and_variables(self):
        first,second=U.InitialNode(),U.ActivityFinalNode()
        flow=U.ControlFlow(source=first,target=second)
        activity=U.Activity(node=[first,second],edge=[flow])
        self.assertTrue(check(flow,'ActivityEdge.source_and_target'))
        self.assertTrue(check(flow,'ActivityEdge.owned'))
        variable=U.Variable(activityScope=activity)
        self.assertTrue(check(variable,'Variable.owned'))
        action=U.OpaqueAction();activity.node.append(action)
        self.assertTrue(variable.isAccessibleBy(action))

    def test_lifeline_ancestor_classifier_and_optional_multivalued_selector(self):
        part=U.Property(upperValue=U.LiteralUnlimitedNatural(value=3));base=U.Class(ownedAttribute=[part])
        child=U.Class(generalization=[U.Generalization(general=base)])
        lifeline=U.Lifeline(represents=part);interaction=U.Interaction(lifeline=[lifeline])
        child.ownedBehavior.append(interaction)
        self.assertTrue(check(lifeline,'Lifeline.same_classifier'))
        self.assertTrue(check(lifeline,'Lifeline.selector_specified'))
        lifeline.selector=U.LiteralInteger(value=1)
        self.assertTrue(check(lifeline,'Lifeline.selector_specified'))
        part.upperValue=U.LiteralUnlimitedNatural(value=1)
        self.assertFalse(check(lifeline,'Lifeline.selector_specified'))

    def test_message_operation_arguments_and_ordering_cycle(self):
        type_=U.Class();operation=U.Operation(name='f',ownedParameter=[U.Parameter(type=type_)])
        message=U.Message(name='f',signature=operation,messageSort=U.MessageSort.synchCall,argument=[U.LiteralInteger(type=type_)])
        self.assertTrue(check(message,'Message.signature_is_operation'))
        message.argument[0].type=U.Class()
        self.assertFalse(check(message,'Message.signature_is_operation'))
        first,second=U.OccurrenceSpecification(),U.OccurrenceSpecification()
        order=U.GeneralOrdering(before=first,after=second)
        self.assertTrue(check(order,'GeneralOrdering.irreflexsive_transitive_closure'))
        U.GeneralOrdering(before=second,after=first)
        self.assertFalse(check(order,'GeneralOrdering.irreflexsive_transitive_closure'))

    def test_implicit_gate_names_and_loop_constraints(self):
        send,receive=U.Gate(),U.Gate()
        inner=U.Interaction(formalGate=[send]);use=U.InteractionUse(refersTo=inner,actualGate=[receive])
        U.Message(name='call',sendEvent=send);U.Message(name='call',receiveEvent=receive)
        self.assertEqual(send.getName(),receive.getName())
        self.assertTrue(check(receive,'Gate.messages_actual_gate'))
        fragment=U.CombinedFragment(interactionOperator=U.InteractionOperatorKind.alt,
                                   operand=[U.InteractionOperand(guard=U.InteractionConstraint(minint=U.LiteralInteger(value=1)))])
        self.assertFalse(check(fragment,'CombinedFragment.minint_and_maxint'))
        fragment.interactionOperator=U.InteractionOperatorKind.loop
        self.assertTrue(check(fragment,'CombinedFragment.minint_and_maxint'))

    def test_usecase_inclusion_and_actor_associations(self):
        first,second=U.UseCase(name='A'),U.UseCase(name='B')
        first.include.append(U.Include(addition=second))
        self.assertEqual(first.allIncludedUseCases(),[second])
        second.include.append(U.Include(addition=first))
        self.assertFalse(check(first,'UseCase.cannot_include_self'))
        actor=U.Actor(name='User');association=U.Association(ownedEnd=[U.Property(type=actor),U.Property(type=first)])
        self.assertTrue(check(actor,'Actor.associations'))
        association.ownedEnd.append(U.Property(type=U.Class()))
        self.assertFalse(check(actor,'Actor.associations'))

    def test_deployments_instances_and_information_flow_channels(self):
        component=U.Component();artifact=U.Artifact(manifestation=[U.Manifestation(utilizedElement=component)])
        instance=U.InstanceSpecification(classifier=[artifact])
        specification=U.DeploymentSpecification()
        target=U.ExecutionEnvironment(deployment=[U.Deployment(deployedArtifact=[instance],configuration=[specification])])
        self.assertEqual(target.deployedElement,[component])
        self.assertTrue(check(specification,'DeploymentSpecification.deployed_elements'))
        source,destination=U.Class(),U.Class()
        channel=U.Dependency(client=[source],supplier=[destination])
        flow=U.InformationFlow(informationSource=[source],informationTarget=[destination],realization=[channel])
        self.assertTrue(check(flow,'InformationFlow.must_conform'))
        channel.supplier=[U.Class()]
        self.assertFalse(check(flow,'InformationFlow.must_conform'))
