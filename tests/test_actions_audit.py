"""Action signatures, pin roles, association ends and structured boundaries."""
import unittest
import Uml
from umltools import ModelSession, UnsupportedSemanticsError
from umltools.native import check, NativeNotImplemented
from umltools.expression_semantics import register_collection_type
from test_activities_audit import bounded
from semantic_cases import verifies


class ActionCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()
        self.t = Uml.Class()
        self.boolean = Uml.PrimitiveType(name='Boolean')
        self.index = Uml.PrimitiveType(name='UnlimitedNatural')

    def tearDown(self): self.session.__exit__(None, None, None)

    def pin(self, cls=Uml.InputPin, **kwargs): return bounded(cls, **kwargs)

    def rules(self, node, *names, expected=True):
        for name in names:
            with self.subTest(rule=name): self.assertEqual(check(node, name), expected)

    @verifies('Action.allActions', 'Action.allOwnedNodes', 'Action.containingBehavior', 'Action.context',
              'Action-input', 'Action-output', 'Variable.isAccessibleBy', 'VariableAction.scope_of_variable',
              'StructuredActivityNode.allActions', 'StructuredActivityNode.allOwnedNodes',
              'StructuredActivityNode.sourceNodes', 'StructuredActivityNode.targetNodes', 'StructuredActivityNode.containingActivity',
              'ConditionalNode.allActions', 'LoopNode.allActions', 'LoopNode.sourceNodes')
    def test_nested_actions_context_variable_scope_and_exposed_pin_unions(self):
        pin, output = self.pin(), self.pin(Uml.OutputPin)
        action = Uml.OpaqueAction(inputValue=[pin], outputValue=[output])
        inner = Uml.StructuredActivityNode(node=[action])
        outer = Uml.StructuredActivityNode(node=[inner])
        activity = Uml.Activity(structuredNode=[outer])
        var = Uml.Variable()
        outer.variable.append(var)
        self.assertTrue(var.isAccessibleBy(action))
        self.assertFalse(var.isAccessibleBy(Uml.OpaqueAction()))
        read = Uml.ReadVariableAction(variable=var)
        inner.node.append(read)
        self.rules(read, 'VariableAction.scope_of_variable')
        inner.node.remove(read)
        self.rules(read, 'VariableAction.scope_of_variable', expected=False)
        self.assertEqual(action.allActions(), [action])
        self.assertEqual(action.input, [pin])
        self.assertEqual(action.output, [output])
        self.assertEqual(set(action.allOwnedNodes()), {pin, output})
        self.assertEqual(set(outer.allActions()), {outer, inner, action})
        self.assertEqual(set(outer.allOwnedNodes()), {inner, action, pin, output})
        self.assertEqual(set(inner.sourceNodes()), {action, output})
        self.assertEqual(set(inner.targetNodes()), {action, pin})
        self.assertIs(outer.containingActivity(), activity)
        self.assertIs(action.containingBehavior(), activity)
        self.assertIs(action.context, activity)
        cls = Uml.Class(ownedBehavior=[activity])
        self.assertIs(action.context, cls)
        for node in (Uml.ConditionalNode(node=[Uml.OpaqueAction()]), Uml.LoopNode(node=[Uml.OpaqueAction()])):
            self.assertEqual(node.allActions(), [node])
        loop = Uml.LoopNode(loopVariable=[self.pin(Uml.OutputPin)])
        self.assertIn(loop.loopVariable[0], loop.sourceNodes())
        interaction_action = Uml.OpaqueAction()
        interaction = Uml.Interaction(action=[interaction_action])
        self.assertIs(interaction_action.containingBehavior(), interaction)
        self.assertIs(interaction_action.context, interaction)
        self.assertIsNone(Uml.OpaqueAction().context)

    @verifies('CallAction.inputParameters', 'CallAction.outputParameters', 'CallBehaviorAction.inputParameters',
              'CallBehaviorAction.outputParameters', 'CallOperationAction.inputParameters', 'CallOperationAction.outputParameters',
              'CallAction.argument_pins', 'CallAction.result_pins', 'CallAction.synchronous_call',
              'CallBehaviorAction.no_onport', 'CallOperationAction.type_target_pin')
    def test_call_direction_order_covariance_and_target_port_interfaces(self):
        params = [bounded(Uml.Parameter, type=self.t, direction=d) for d in
                  (Uml.ParameterDirectionKind.in_, Uml.ParameterDirectionKind.inout, Uml.ParameterDirectionKind.return_)]
        behavior = Uml.OpaqueBehavior(ownedParameter=params)
        action = Uml.CallBehaviorAction(behavior=behavior, argument=[self.pin(type=self.t), self.pin(type=self.t)],
                                        result=[self.pin(Uml.OutputPin, type=self.t), self.pin(Uml.OutputPin, type=self.t)])
        self.assertEqual(action.inputParameters(), params[:2])
        self.assertEqual(action.outputParameters(), params[1:])
        self.rules(action, 'CallAction.argument_pins', 'CallAction.result_pins', 'CallAction.synchronous_call', 'CallBehaviorAction.no_onport')
        action.isSynchronous = False
        self.rules(action, 'CallAction.synchronous_call', expected=False)
        action.argument[0].type = Uml.Class()
        self.rules(action, 'CallAction.argument_pins', expected=False)
        action.result.reverse()
        action.result[0].upperValue.value = 0
        self.rules(action, 'CallAction.result_pins', expected=False)
        action.onPort = Uml.Port()
        self.rules(action, 'CallBehaviorAction.no_onport', expected=False)
        operation = Uml.Operation(ownedParameter=[bounded(Uml.Parameter, type=self.t),
                                                  bounded(Uml.Parameter, type=self.t, direction=Uml.ParameterDirectionKind.out)])
        target_type = Uml.Class(ownedOperation=[operation])
        call = Uml.CallOperationAction(operation=operation, target=self.pin(type=target_type))
        self.assertEqual(call.inputParameters(), operation.ownedParameter[:1])
        self.assertEqual(call.outputParameters(), operation.ownedParameter[1:])
        self.rules(call, 'CallOperationAction.type_target_pin')
        call.target.type = Uml.Class()
        self.rules(call, 'CallOperationAction.type_target_pin', expected=False)
        interface = Uml.Interface(ownedOperation=[Uml.Operation()])
        port = Uml.Port(type=interface)
        call.target.type.ownedAttribute.append(port)
        call.operation, call.onPort = interface.ownedOperation[0], port
        self.rules(call, 'CallOperationAction.type_target_pin')
        # Explicit abstract declarations remain unsupported, even when called on a concrete instance.
        for name in ('inputParameters', 'outputParameters'):
            with self.assertRaises(UnsupportedSemanticsError): action.uml_operation('CallAction', name)

    @verifies('AcceptCallAction.result_pins', 'AcceptCallAction.trigger_call_event', 'AcceptCallAction.unmarshall',
              'AcceptEventAction.one_output_pin', 'AcceptEventAction.no_input_pins', 'AcceptEventAction.no_output_pins',
              'AcceptEventAction.unmarshall_signal_events', 'AcceptEventAction.conforming_type',
              'ReplyAction.pins_match_parameter', 'ReplyAction.event_on_reply_to_call_trigger')
    def test_accept_call_signal_change_and_reply(self):
        op = Uml.Operation(ownedParameter=[bounded(Uml.Parameter, type=self.t),
                                           bounded(Uml.Parameter, type=self.t, direction=Uml.ParameterDirectionKind.return_)])
        trigger = Uml.Trigger(event=Uml.CallEvent(operation=op))
        accept = Uml.AcceptCallAction(trigger=[trigger], result=[self.pin(Uml.OutputPin, type=self.t)], isUnmarshall=True)
        self.rules(accept, 'AcceptCallAction.result_pins', 'AcceptCallAction.trigger_call_event', 'AcceptCallAction.unmarshall')
        accept.isUnmarshall = False
        self.rules(accept, 'AcceptCallAction.unmarshall', expected=False)
        accept.result[0].type = Uml.Class()
        self.rules(accept, 'AcceptCallAction.result_pins', expected=False)
        reply = Uml.ReplyAction(replyToCall=trigger, replyValue=[self.pin(type=self.t)])
        self.rules(reply, 'ReplyAction.pins_match_parameter', 'ReplyAction.event_on_reply_to_call_trigger')
        reply.replyValue[0].type = Uml.Class()
        self.rules(reply, 'ReplyAction.pins_match_parameter', expected=False)
        trigger.event = Uml.ChangeEvent()
        self.rules(accept, 'AcceptCallAction.trigger_call_event', expected=False)
        self.rules(reply, 'ReplyAction.event_on_reply_to_call_trigger', expected=False)
        signal = Uml.Signal(ownedAttribute=[bounded(Uml.Property, type=self.t)])
        event = Uml.AcceptEventAction(trigger=[Uml.Trigger(event=Uml.SignalEvent(signal=signal))],
                                      result=[self.pin(Uml.OutputPin, type=signal)])
        self.rules(event, 'AcceptEventAction.one_output_pin', 'AcceptEventAction.no_input_pins', 'AcceptEventAction.conforming_type')
        event.result[0].type = Uml.Class()
        self.rules(event, 'AcceptEventAction.conforming_type', expected=False)
        event.isUnmarshall = True
        event.result[0].type = self.t
        self.rules(event, 'AcceptEventAction.unmarshall_signal_events')
        event.result[0].type = Uml.Class()
        self.rules(event, 'AcceptEventAction.unmarshall_signal_events', expected=False)
        event.isUnmarshall = False
        event.result.clear()
        self.rules(event, 'AcceptEventAction.one_output_pin', expected=False)
        event.trigger[0].event = Uml.ChangeEvent()
        self.rules(event, 'AcceptEventAction.no_output_pins')
        event.result.append(self.pin(Uml.OutputPin))
        self.rules(event, 'AcceptEventAction.no_output_pins', expected=False)

    @verifies('BroadcastSignalAction.number_of_arguments', 'BroadcastSignalAction.type_ordering_multiplicity',
              'BroadcastSignalAction.no_onport', 'SendSignalAction.number_order', 'SendSignalAction.type_ordering_multiplicity',
              'SendSignalAction.type_target_pin', 'SendObjectAction.type_target_pin')
    def test_signal_arguments_and_port_membership(self):
        signal = Uml.Signal(ownedAttribute=[bounded(Uml.Property, type=self.t)])
        for cls, prefix in ((Uml.BroadcastSignalAction, 'BroadcastSignalAction'), (Uml.SendSignalAction, 'SendSignalAction')):
            action = cls(signal=signal, argument=[self.pin(type=self.t)])
            count = prefix + ('.number_of_arguments' if cls is Uml.BroadcastSignalAction else '.number_order')
            self.rules(action, count, prefix+'.type_ordering_multiplicity')
            action.argument[0].type = Uml.Class()
            self.rules(action, prefix+'.type_ordering_multiplicity', expected=False)
            action.argument.clear()
            self.rules(action, count, expected=False)
            if cls is Uml.BroadcastSignalAction:
                self.rules(action, 'BroadcastSignalAction.no_onport')
                action.onPort = Uml.Port()
                self.rules(action, 'BroadcastSignalAction.no_onport', expected=False)
        t, port = Uml.Class(), Uml.Port()
        t.ownedAttribute.append(port)
        for cls, rule in ((Uml.SendSignalAction,'SendSignalAction.type_target_pin'), (Uml.SendObjectAction,'SendObjectAction.type_target_pin')):
            a = cls(target=self.pin(type=t), onPort=port)
            self.rules(a, rule)
            a.onPort = Uml.Port()
            self.rules(a, rule, expected=False)

    @verifies('ValueSpecificationAction.multiplicity', 'ValueSpecificationAction.compatible_type',
              'CreateObjectAction.classifier_not_abstract', 'CreateObjectAction.classifier_not_association_class',
              'CreateObjectAction.multiplicity', 'CreateObjectAction.same_type', 'DestroyObjectAction.multiplicity',
              'DestroyObjectAction.no_type', 'ReadExtentAction.type_is_classifier', 'ReadExtentAction.multiplicity_of_result',
              'ReadIsClassifiedObjectAction.no_type', 'ReadIsClassifiedObjectAction.multiplicity_of_input',
              'ReadIsClassifiedObjectAction.multiplicity_of_output', 'ReadIsClassifiedObjectAction.boolean_result',
              'ReclassifyObjectAction.input_pin', 'ReclassifyObjectAction.classifier_not_abstract', 'ReclassifyObjectAction.multiplicity',
              'TestIdentityAction.multiplicity', 'TestIdentityAction.no_type', 'TestIdentityAction.result_is_boolean')
    def test_object_creation_extent_identity_and_classification(self):
        value = Uml.ValueSpecificationAction(value=Uml.LiteralInteger(type=self.t, value=1), result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(value, 'ValueSpecificationAction.multiplicity', 'ValueSpecificationAction.compatible_type')
        value.result.type = Uml.Class()
        self.rules(value, 'ValueSpecificationAction.compatible_type', expected=False)
        value.result.upperValue.value = 2
        self.rules(value, 'ValueSpecificationAction.multiplicity', expected=False)
        create = Uml.CreateObjectAction(classifier=self.t, result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(create, 'CreateObjectAction.classifier_not_abstract', 'CreateObjectAction.classifier_not_association_class', 'CreateObjectAction.multiplicity', 'CreateObjectAction.same_type')
        self.t.isAbstract = True
        self.rules(create, 'CreateObjectAction.classifier_not_abstract', expected=False)
        create.classifier = Uml.AssociationClass()
        self.rules(create, 'CreateObjectAction.classifier_not_association_class', 'CreateObjectAction.same_type', expected=False)
        extent = Uml.ReadExtentAction(classifier=self.t, result=bounded(Uml.OutputPin, 0, float('inf'), type=self.t))
        self.rules(extent, 'ReadExtentAction.type_is_classifier', 'ReadExtentAction.multiplicity_of_result')
        extent.result.type, extent.result.upperValue.value = Uml.Class(), 1
        self.rules(extent, 'ReadExtentAction.type_is_classifier', 'ReadExtentAction.multiplicity_of_result', expected=False)
        destroy = Uml.DestroyObjectAction(target=self.pin())
        classified = Uml.ReadIsClassifiedObjectAction(object=self.pin(), result=self.pin(Uml.OutputPin, type=self.boolean))
        reclassify = Uml.ReclassifyObjectAction(object=self.pin(), newClassifier=[Uml.Class()])
        identity = Uml.TestIdentityAction(first=self.pin(), second=self.pin(), result=self.pin(Uml.OutputPin, type=self.boolean))
        for a, rules in ((destroy, ('DestroyObjectAction.no_type','DestroyObjectAction.multiplicity')),
                         (classified, ('ReadIsClassifiedObjectAction.no_type','ReadIsClassifiedObjectAction.multiplicity_of_input','ReadIsClassifiedObjectAction.multiplicity_of_output','ReadIsClassifiedObjectAction.boolean_result')),
                         (reclassify, ('ReclassifyObjectAction.input_pin','ReclassifyObjectAction.multiplicity','ReclassifyObjectAction.classifier_not_abstract')),
                         (identity, ('TestIdentityAction.no_type','TestIdentityAction.multiplicity','TestIdentityAction.result_is_boolean'))): self.rules(a, *rules)
        reclassify.newClassifier[0].isAbstract = True
        self.rules(reclassify, 'ReclassifyObjectAction.classifier_not_abstract', expected=False)
        destroy.target.type = classified.object.type = reclassify.object.type = identity.first.type = self.t
        for a, rule in ((destroy,'DestroyObjectAction.no_type'),(classified,'ReadIsClassifiedObjectAction.no_type'),
                        (reclassify,'ReclassifyObjectAction.input_pin'),(identity,'TestIdentityAction.no_type')): self.rules(a, rule, expected=False)
        identity.result.type = classified.result.type = self.t
        self.rules(identity, 'TestIdentityAction.result_is_boolean', expected=False)
        self.rules(classified, 'ReadIsClassifiedObjectAction.boolean_result', expected=False)

    @verifies('StructuralFeatureAction.multiplicity', 'StructuralFeatureAction.object_type', 'StructuralFeatureAction.visibility',
              'StructuralFeatureAction.not_static', 'StructuralFeatureAction.one_featuring_classifier',
              'ReadStructuralFeatureAction.multiplicity', 'ReadStructuralFeatureAction.type_and_ordering',
              'WriteStructuralFeatureAction.multiplicity_of_result', 'WriteStructuralFeatureAction.type_of_value',
              'WriteStructuralFeatureAction.multiplicity_of_value', 'WriteStructuralFeatureAction.type_of_result',
              'AddStructuralFeatureValueAction.required_value', 'AddStructuralFeatureValueAction.insertAt_pin',
              'RemoveStructuralFeatureValueAction.removeAt_and_value', 'ClearStructuralFeatureAction.type_of_result',
              'ClearStructuralFeatureAction.multiplicity_of_result')
    def test_structural_feature_single_classifier_visibility_and_index_roles(self):
        feature = bounded(Uml.Property, type=self.t, visibility=Uml.VisibilityKind.public)
        cls = Uml.Class(ownedAttribute=[feature])
        read = Uml.ReadStructuralFeatureAction(structuralFeature=feature, object=self.pin(type=cls), result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(read, 'StructuralFeatureAction.multiplicity', 'StructuralFeatureAction.object_type',
                   'StructuralFeatureAction.visibility', 'StructuralFeatureAction.not_static', 'StructuralFeatureAction.one_featuring_classifier',
                   'ReadStructuralFeatureAction.multiplicity', 'ReadStructuralFeatureAction.type_and_ordering')
        feature.isStatic = True
        self.rules(read, 'StructuralFeatureAction.not_static', expected=False)
        feature.isStatic = False
        read.result.type = Uml.Class()
        self.rules(read, 'ReadStructuralFeatureAction.type_and_ordering', expected=False)
        read.result.upperValue.value = 0
        self.rules(read, 'ReadStructuralFeatureAction.multiplicity', expected=False)
        add = Uml.AddStructuralFeatureValueAction(structuralFeature=feature, object=self.pin(type=cls),
                                                   value=self.pin(type=self.t), result=self.pin(Uml.OutputPin, type=cls))
        self.rules(add, 'WriteStructuralFeatureAction.multiplicity_of_result', 'WriteStructuralFeatureAction.type_of_value',
                   'WriteStructuralFeatureAction.multiplicity_of_value', 'WriteStructuralFeatureAction.type_of_result',
                   'AddStructuralFeatureValueAction.required_value', 'AddStructuralFeatureValueAction.insertAt_pin')
        feature.isOrdered = True
        self.rules(add, 'AddStructuralFeatureValueAction.insertAt_pin', expected=False)
        add.insertAt = self.pin(type=self.index)
        self.rules(add, 'AddStructuralFeatureValueAction.insertAt_pin')
        add.value.type, add.result.type = Uml.Class(), self.t
        self.rules(add, 'WriteStructuralFeatureAction.type_of_value', 'WriteStructuralFeatureAction.type_of_result', expected=False)
        add.value.upperValue.value = add.result.upperValue.value = 2
        self.rules(add, 'WriteStructuralFeatureAction.multiplicity_of_value', 'WriteStructuralFeatureAction.multiplicity_of_result', expected=False)
        add.value = None
        self.rules(add, 'AddStructuralFeatureValueAction.required_value', expected=False)
        remove = Uml.RemoveStructuralFeatureValueAction(structuralFeature=feature, object=self.pin(type=cls), value=self.pin())
        self.rules(remove, 'RemoveStructuralFeatureValueAction.removeAt_and_value')
        feature.isUnique = False
        self.rules(remove, 'RemoveStructuralFeatureValueAction.removeAt_and_value', expected=False)
        remove.value, remove.removeAt = None, self.pin(type=self.index)
        self.rules(remove, 'RemoveStructuralFeatureValueAction.removeAt_and_value')
        clear = Uml.ClearStructuralFeatureAction(object=self.pin(type=cls), structuralFeature=feature, result=self.pin(Uml.OutputPin, type=cls))
        self.rules(clear, 'ClearStructuralFeatureAction.type_of_result', 'ClearStructuralFeatureAction.multiplicity_of_result')
        clear.result.type, clear.result.upperValue.value = self.t, 2
        self.rules(clear, 'ClearStructuralFeatureAction.type_of_result', 'ClearStructuralFeatureAction.multiplicity_of_result', expected=False)
        cls.ownedAttribute.remove(feature)
        self.rules(read, 'StructuralFeatureAction.one_featuring_classifier', expected=False)

    @verifies('WriteVariableAction.value_type', 'WriteVariableAction.multiplicity', 'AddVariableValueAction.required_value',
              'AddVariableValueAction.insertAt_pin', 'RemoveVariableValueAction.removeAt_and_value',
              'ReadVariableAction.type_and_ordering', 'ReadVariableAction.compatible_multiplicity')
    def test_variable_read_write_remove_and_ordered_insert(self):
        variable = bounded(Uml.Variable, type=self.t)
        read = Uml.ReadVariableAction(variable=variable, result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(read, 'ReadVariableAction.type_and_ordering', 'ReadVariableAction.compatible_multiplicity')
        read.result.type, read.result.upperValue.value = Uml.Class(), 0
        self.rules(read, 'ReadVariableAction.type_and_ordering', 'ReadVariableAction.compatible_multiplicity', expected=False)
        add = Uml.AddVariableValueAction(variable=variable, value=self.pin(type=self.t))
        self.rules(add, 'WriteVariableAction.value_type', 'WriteVariableAction.multiplicity', 'AddVariableValueAction.required_value', 'AddVariableValueAction.insertAt_pin')
        add.value.type, add.value.upperValue.value = Uml.Class(), 2
        self.rules(add, 'WriteVariableAction.value_type', 'WriteVariableAction.multiplicity', expected=False)
        add.value = None
        self.rules(add, 'AddVariableValueAction.required_value', expected=False)
        variable.isOrdered = True
        self.rules(add, 'AddVariableValueAction.insertAt_pin', expected=False)
        add.insertAt = self.pin(type=self.index)
        self.rules(add, 'AddVariableValueAction.insertAt_pin')
        remove = Uml.RemoveVariableValueAction(variable=variable, value=self.pin())
        self.rules(remove, 'RemoveVariableValueAction.removeAt_and_value')
        variable.isUnique = False
        self.rules(remove, 'RemoveVariableValueAction.removeAt_and_value', expected=False)
        remove.value, remove.removeAt = None, self.pin(type=self.index)
        self.rules(remove, 'RemoveVariableValueAction.removeAt_and_value')

    @verifies('StartObjectBehaviorAction.behavior', 'StartObjectBehaviorAction.inputParameters', 'StartObjectBehaviorAction.outputParameters',
              'StartObjectBehaviorAction.multiplicity_of_object', 'StartObjectBehaviorAction.type_of_object', 'StartObjectBehaviorAction.no_onport',
              'StartClassifierBehaviorAction.multiplicity', 'StartClassifierBehaviorAction.type_has_classifier',
              'ReadSelfAction.contained', 'ReadSelfAction.multiplicity', 'ReadSelfAction.not_static', 'ReadSelfAction.type')
    def test_classifier_behavior_resolution_and_read_self_context(self):
        behavior = Uml.OpaqueBehavior(ownedParameter=[Uml.Parameter(), Uml.Parameter(direction=Uml.ParameterDirectionKind.return_)])
        cls = Uml.Class(ownedBehavior=[behavior], classifierBehavior=behavior)
        start = Uml.StartObjectBehaviorAction(object=self.pin(type=cls))
        self.assertIs(start.behavior(), behavior)
        self.assertEqual(start.inputParameters(), behavior.ownedParameter[:1])
        self.assertEqual(start.outputParameters(), behavior.ownedParameter[1:])
        self.rules(start, 'StartObjectBehaviorAction.multiplicity_of_object', 'StartObjectBehaviorAction.type_of_object', 'StartObjectBehaviorAction.no_onport')
        start.object.type = behavior
        self.assertIs(start.behavior(), behavior)
        start.object.type = Uml.DataType()
        self.assertIsNone(start.behavior())
        self.rules(start, 'StartObjectBehaviorAction.type_of_object', expected=False)
        start.onPort = Uml.Port()
        self.rules(start, 'StartObjectBehaviorAction.no_onport', expected=False)
        classifier_start = Uml.StartClassifierBehaviorAction(object=self.pin(type=cls))
        self.rules(classifier_start, 'StartClassifierBehaviorAction.multiplicity', 'StartClassifierBehaviorAction.type_has_classifier')
        classifier_start.object.type = Uml.Class()
        self.rules(classifier_start, 'StartClassifierBehaviorAction.type_has_classifier', expected=False)
        read = Uml.ReadSelfAction(result=self.pin(Uml.OutputPin, type=cls))
        activity = Uml.Activity(node=[read])
        cls.ownedBehavior.append(activity)
        self.rules(read, 'ReadSelfAction.contained', 'ReadSelfAction.multiplicity', 'ReadSelfAction.not_static', 'ReadSelfAction.type')
        op = Uml.Operation(isStatic=True)
        cls.ownedOperation.append(op)
        activity.specification = op
        self.rules(read, 'ReadSelfAction.not_static', expected=False)
        read.result.type = Uml.Class()
        self.rules(read, 'ReadSelfAction.type', expected=False)
        activity.node.remove(read)
        self.rules(read, 'ReadSelfAction.contained', expected=False)

    @verifies('ActionInputPin.input_pin', 'ActionInputPin.one_output_pin', 'ActionInputPin.no_control_or_object_flow',
              'ValuePin.no_incoming_edges', 'ValuePin.compatible_type', 'Pin.control_pins', 'Pin.not_unique', 'OpaqueAction.language_body_size')
    def test_computed_pins_forbid_producer_edges_and_value_pins_forbid_incoming(self):
        producer = Uml.OpaqueAction(outputValue=[self.pin(Uml.OutputPin)])
        pin = Uml.ActionInputPin(fromAction=producer)
        self.rules(pin, 'ActionInputPin.input_pin', 'ActionInputPin.one_output_pin', 'ActionInputPin.no_control_or_object_flow')
        edge = Uml.ControlFlow(source=producer, target=Uml.ActivityFinalNode())
        self.rules(pin, 'ActionInputPin.no_control_or_object_flow', expected=False)
        edge.delete()
        producer.inputValue.append(self.pin())
        self.rules(pin, 'ActionInputPin.input_pin', expected=False)
        producer.outputValue.clear()
        self.rules(pin, 'ActionInputPin.one_output_pin', expected=False)
        value = Uml.ValuePin(type=self.t, value=Uml.LiteralInteger(type=self.t))
        self.rules(value, 'ValuePin.no_incoming_edges', 'ValuePin.compatible_type')
        value.value.type = Uml.Class()
        self.rules(value, 'ValuePin.compatible_type', expected=False)
        Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=value)
        self.rules(value, 'ValuePin.no_incoming_edges', expected=False)
        value.isControl, value.isControlType, value.isUnique = True, True, False
        self.rules(value, 'Pin.control_pins', 'Pin.not_unique')
        value.isControlType, value.isUnique = False, True
        self.rules(value, 'Pin.control_pins', 'Pin.not_unique', expected=False)
        action = Uml.OpaqueAction(body=['a'], language=['python'])
        self.rules(action, 'OpaqueAction.language_body_size')
        action.body.append('b')
        self.rules(action, 'OpaqueAction.language_body_size', expected=False)

    @verifies('UnmarshallAction.structural_feature', 'UnmarshallAction.number_of_result', 'UnmarshallAction.type_ordering_and_multiplicity',
              'UnmarshallAction.multiplicity_of_object', 'UnmarshallAction.object_type',
              'ReduceAction.reducer_inputs_output', 'ReduceAction.input_type_is_collection', 'ReduceAction.output_types_are_compatible')
    def test_unmarshall_attribute_order_and_reduce_token_vs_collection_type(self):
        cls = Uml.Class(ownedAttribute=[bounded(Uml.Property, type=self.t)])
        action = Uml.UnmarshallAction(unmarshallType=cls, object=self.pin(type=cls), result=[self.pin(Uml.OutputPin, type=self.t)])
        self.rules(action, 'UnmarshallAction.structural_feature', 'UnmarshallAction.number_of_result', 'UnmarshallAction.type_ordering_and_multiplicity',
                   'UnmarshallAction.multiplicity_of_object', 'UnmarshallAction.object_type')
        action.result[0].type = Uml.Class()
        self.rules(action, 'UnmarshallAction.type_ordering_and_multiplicity', expected=False)
        action.object.type = Uml.Class()
        self.rules(action, 'UnmarshallAction.object_type', expected=False)
        action.result.clear()
        self.rules(action, 'UnmarshallAction.number_of_result', expected=False)
        cls.ownedAttribute.clear()
        self.rules(action, 'UnmarshallAction.structural_feature', expected=False)
        reducer = Uml.OpaqueBehavior(ownedParameter=[bounded(Uml.Parameter, type=self.t), bounded(Uml.Parameter, type=self.t),
                                                     bounded(Uml.Parameter, type=self.t, direction=Uml.ParameterDirectionKind.return_)])
        reduce = Uml.ReduceAction(reducer=reducer, collection=bounded(Uml.InputPin, 0, float('inf'), type=self.t), result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(reduce, 'ReduceAction.reducer_inputs_output', 'ReduceAction.input_type_is_collection', 'ReduceAction.output_types_are_compatible')
        reducer.ownedParameter[2].type = Uml.Class()
        self.rules(reduce, 'ReduceAction.reducer_inputs_output', 'ReduceAction.output_types_are_compatible', expected=False)
        reduce.collection.upperValue.value = 1
        with self.assertRaises(NativeNotImplemented): check(reduce, 'ReduceAction.input_type_is_collection')
        register_collection_type(self.t)
        self.rules(reduce, 'ReduceAction.input_type_is_collection')

    @verifies('LinkAction.association', 'LinkAction.same_pins', 'LinkAction.same_association', 'LinkAction.not_static',
              'LinkEndData.allPins', 'LinkEndData.same_type', 'LinkEndData.multiplicity', 'LinkEndData.end_object_input_pin',
              'LinkEndData.property_is_association_end', 'LinkEndData.qualifiers', 'QualifierValue.multiplicity_of_qualifier',
              'QualifierValue.type_of_qualifier', 'QualifierValue.qualifier_attribute', 'CreateLinkAction.association_not_abstract',
              'LinkEndCreationData.allPins', 'LinkEndCreationData.insertAt_pin', 'LinkEndDestructionData.allPins',
              'LinkEndDestructionData.destroyAt_pin', 'WriteLinkAction.allow_access',
              'ClearAssociationAction.multiplicity', 'ClearAssociationAction.same_type')
    def test_link_end_bags_qualifiers_and_ordered_creation_destruction(self):
        qualifier = bounded(Uml.Property, type=self.t)
        end = bounded(Uml.Property, type=self.t, qualifier=[qualifier], visibility=Uml.VisibilityKind.public)
        other = bounded(Uml.Property, type=self.t)
        association = Uml.Association(ownedEnd=[end, other])
        value, qpin = self.pin(type=self.t), self.pin(type=self.t)
        qvalue = Uml.QualifierValue(qualifier=qualifier, value=qpin)
        data = Uml.LinkEndCreationData(end=end, value=value, qualifier=[qvalue])
        data2 = Uml.LinkEndCreationData(end=other, value=self.pin(type=self.t))
        action = Uml.CreateLinkAction(endData=[data, data2], inputValue=[value, qpin, data2.value])
        self.assertIs(action.association(), association)
        self.assertEqual(data.allPins(), [value, qpin])
        self.assertEqual(data.uml_operation('LinkEndData', 'allPins'), [value, qpin])
        self.rules(action, 'LinkAction.same_pins', 'LinkAction.same_association', 'LinkAction.not_static',
                   'CreateLinkAction.association_not_abstract', 'WriteLinkAction.allow_access')
        self.rules(data, 'LinkEndData.same_type', 'LinkEndData.multiplicity', 'LinkEndData.end_object_input_pin',
                   'LinkEndData.property_is_association_end', 'LinkEndData.qualifiers', 'LinkEndCreationData.insertAt_pin')
        self.rules(qvalue, 'QualifierValue.multiplicity_of_qualifier', 'QualifierValue.type_of_qualifier', 'QualifierValue.qualifier_attribute')
        qpin.type = Uml.Class()
        self.rules(qvalue, 'QualifierValue.type_of_qualifier', expected=False)
        qvalue.qualifier = bounded(Uml.Property)
        self.rules(qvalue, 'QualifierValue.qualifier_attribute', expected=False)
        self.rules(data, 'LinkEndData.qualifiers', expected=False)
        qvalue.qualifier = qualifier
        data.value = qpin
        # allPins is a bag, so a pin in two roles occurs twice and cannot be
        # represented by the unique LinkAction.inputValue set without a violation.
        self.assertEqual(data.allPins(), [qpin, qpin])
        self.rules(data, 'LinkEndData.end_object_input_pin', expected=False)
        self.rules(action, 'LinkAction.same_pins', expected=False)
        data.value = value
        value.type, value.upperValue.value = Uml.Class(), 2
        self.rules(data, 'LinkEndData.same_type', 'LinkEndData.multiplicity', expected=False)
        end.isStatic = association.isAbstract = True
        self.rules(action, 'LinkAction.not_static', 'CreateLinkAction.association_not_abstract', expected=False)
        end.isOrdered = True
        self.rules(data, 'LinkEndCreationData.insertAt_pin', expected=False)
        data.insertAt = self.pin(type=self.index)
        self.rules(data, 'LinkEndCreationData.insertAt_pin')
        self.assertIn(data.insertAt, data.allPins())
        destroy = Uml.LinkEndDestructionData(end=end, value=self.pin(), destroyAt=self.pin(type=self.index))
        self.rules(destroy, 'LinkEndDestructionData.destroyAt_pin', expected=False)  # Unique end forbids an index.
        end.isUnique = False
        self.rules(destroy, 'LinkEndDestructionData.destroyAt_pin')
        self.assertIn(destroy.destroyAt, destroy.allPins())
        destroy.destroyAt = None
        self.rules(destroy, 'LinkEndDestructionData.destroyAt_pin', expected=False)
        destroy.isDestroyDuplicates = True
        self.rules(destroy, 'LinkEndDestructionData.destroyAt_pin')
        action.endData.remove(data2)
        self.rules(action, 'LinkAction.same_association', expected=False)
        clear = Uml.ClearAssociationAction(association=association, object=self.pin(type=self.t))
        self.rules(clear, 'ClearAssociationAction.multiplicity', 'ClearAssociationAction.same_type')
        clear.object.type = Uml.Class()
        self.rules(clear, 'ClearAssociationAction.same_type', expected=False)

    @verifies('ReadLinkAction.openEnd', 'ReadLinkAction.type_and_ordering', 'ReadLinkAction.compatible_multiplicity',
              'ReadLinkAction.visibility', 'ReadLinkAction.one_open_end', 'ReadLinkAction.navigable_open_end',
              'CreateLinkObjectAction.multiplicity', 'CreateLinkObjectAction.type_of_result', 'CreateLinkObjectAction.association_class',
              'ReadLinkObjectEndAction.property', 'ReadLinkObjectEndAction.multiplicity_of_object',
              'ReadLinkObjectEndAction.ends_of_association', 'ReadLinkObjectEndAction.type_of_result',
              'ReadLinkObjectEndAction.multiplicity_of_result', 'ReadLinkObjectEndAction.type_of_object',
              'ReadLinkObjectEndAction.association_of_association', 'ReadLinkObjectEndQualifierAction.multiplicity_of_object',
              'ReadLinkObjectEndQualifierAction.type_of_object', 'ReadLinkObjectEndQualifierAction.multiplicity_of_qualifier',
              'ReadLinkObjectEndQualifierAction.ends_of_association', 'ReadLinkObjectEndQualifierAction.multiplicity_of_result',
              'ReadLinkObjectEndQualifierAction.same_type', 'ReadLinkObjectEndQualifierAction.association_of_association',
              'ReadLinkObjectEndQualifierAction.qualifier_attribute')
    def test_open_link_end_navigation_and_association_class_qualifier_reads(self):
        qualifier = bounded(Uml.Property, type=self.t)
        end = bounded(Uml.Property, type=self.t, qualifier=[qualifier], visibility=Uml.VisibilityKind.public)
        other = bounded(Uml.Property, type=self.t)
        association = Uml.AssociationClass(ownedEnd=[end, other], navigableOwnedEnd=[end])
        read = Uml.ReadLinkAction(endData=[Uml.LinkEndData(end=end), Uml.LinkEndData(end=other, value=self.pin())],
                                  result=self.pin(Uml.OutputPin, type=self.t))
        self.assertEqual(read.openEnd(), [end])
        self.rules(read, 'ReadLinkAction.type_and_ordering', 'ReadLinkAction.compatible_multiplicity',
                   'ReadLinkAction.visibility', 'ReadLinkAction.one_open_end', 'ReadLinkAction.navigable_open_end')
        read.result.type, read.result.upperValue.value = Uml.Class(), 0
        self.rules(read, 'ReadLinkAction.type_and_ordering', 'ReadLinkAction.compatible_multiplicity', expected=False)
        association.navigableOwnedEnd.clear()
        self.rules(read, 'ReadLinkAction.navigable_open_end', expected=False)
        read.endData[1].value = None
        self.rules(read, 'ReadLinkAction.one_open_end', expected=False)
        create = Uml.CreateLinkObjectAction(endData=[Uml.LinkEndCreationData(end=end)], result=self.pin(Uml.OutputPin, type=association))
        self.rules(create, 'CreateLinkObjectAction.multiplicity', 'CreateLinkObjectAction.type_of_result', 'CreateLinkObjectAction.association_class')
        create.result.type = self.t
        self.rules(create, 'CreateLinkObjectAction.type_of_result', expected=False)
        endread = Uml.ReadLinkObjectEndAction(end=end, object=self.pin(type=association), result=self.pin(Uml.OutputPin, type=self.t))
        qread = Uml.ReadLinkObjectEndQualifierAction(qualifier=qualifier, object=self.pin(type=association), result=self.pin(Uml.OutputPin, type=self.t))
        self.rules(endread, 'ReadLinkObjectEndAction.property', 'ReadLinkObjectEndAction.multiplicity_of_object',
                   'ReadLinkObjectEndAction.ends_of_association', 'ReadLinkObjectEndAction.type_of_result',
                   'ReadLinkObjectEndAction.multiplicity_of_result', 'ReadLinkObjectEndAction.type_of_object', 'ReadLinkObjectEndAction.association_of_association')
        self.rules(qread, 'ReadLinkObjectEndQualifierAction.multiplicity_of_object', 'ReadLinkObjectEndQualifierAction.type_of_object',
                   'ReadLinkObjectEndQualifierAction.multiplicity_of_qualifier', 'ReadLinkObjectEndQualifierAction.ends_of_association',
                   'ReadLinkObjectEndQualifierAction.multiplicity_of_result', 'ReadLinkObjectEndQualifierAction.same_type',
                   'ReadLinkObjectEndQualifierAction.association_of_association', 'ReadLinkObjectEndQualifierAction.qualifier_attribute')
        other.isStatic = True
        self.rules(endread, 'ReadLinkObjectEndAction.ends_of_association', expected=False)
        self.rules(qread, 'ReadLinkObjectEndQualifierAction.ends_of_association', expected=False)
        endread.result.type = qread.result.type = Uml.Class()
        self.rules(endread, 'ReadLinkObjectEndAction.type_of_result', expected=False)
        self.rules(qread, 'ReadLinkObjectEndQualifierAction.same_type', expected=False)
        endread.object.type = qread.object.type = self.t
        self.rules(endread, 'ReadLinkObjectEndAction.type_of_object', expected=False)
        self.rules(qread, 'ReadLinkObjectEndQualifierAction.type_of_object', expected=False)

    @verifies('Clause.body_output_pins', 'Clause.decider_output', 'Clause.test_and_body', 'ConditionalNode.result_no_incoming',
              'ConditionalNode.no_input_pins', 'ConditionalNode.one_clause_with_executable_node',
              'ConditionalNode.matching_output_pins', 'ConditionalNode.executable_nodes', 'ConditionalNode.clause_no_predecessor')
    def test_conditional_clause_membership_signatures_and_predecessor_cycles(self):
        decider = self.pin(Uml.OutputPin, type=self.boolean)
        test = Uml.OpaqueAction(outputValue=[decider])
        output = self.pin(Uml.OutputPin, type=self.t)
        body = Uml.OpaqueAction(outputValue=[output])
        clause = Uml.Clause(test=[test], body=[body], bodyOutput=[output], decider=decider)
        node = Uml.ConditionalNode(node=[test, body], clause=[clause], result=[self.pin(Uml.OutputPin, type=self.t)])
        self.rules(clause, 'Clause.body_output_pins', 'Clause.decider_output', 'Clause.test_and_body')
        self.rules(node, 'ConditionalNode.result_no_incoming', 'ConditionalNode.no_input_pins', 'ConditionalNode.one_clause_with_executable_node',
                   'ConditionalNode.matching_output_pins', 'ConditionalNode.executable_nodes', 'ConditionalNode.clause_no_predecessor')
        second = Uml.Clause(predecessorClause=[clause])
        node.clause.append(second)
        self.rules(node, 'ConditionalNode.clause_no_predecessor')
        clause.predecessorClause.append(second)
        self.rules(node, 'ConditionalNode.clause_no_predecessor', expected=False)
        clause.body.append(test)
        self.rules(clause, 'Clause.test_and_body', expected=False)
        decider.type = self.t
        self.rules(clause, 'Clause.decider_output', expected=False)
        body.outputValue.remove(output)
        self.rules(clause, 'Clause.body_output_pins', expected=False)
        node.result[0].type = Uml.Class()
        self.rules(node, 'ConditionalNode.matching_output_pins', expected=False)
        node.node.append(Uml.OpaqueAction())
        self.rules(node, 'ConditionalNode.one_clause_with_executable_node', 'ConditionalNode.executable_nodes', expected=False)
        Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=node.result[0])
        self.rules(node, 'ConditionalNode.result_no_incoming', expected=False)
        node.structuredNodeInput.append(self.pin())
        self.rules(node, 'ConditionalNode.no_input_pins', expected=False)

    @verifies('LoopNode.result_no_incoming', 'LoopNode.input_edges', 'LoopNode.executable_nodes', 'LoopNode.body_output_pins',
              'LoopNode.setup_test_and_body', 'LoopNode.matching_output_pins', 'LoopNode.matching_loop_variables',
              'LoopNode.matching_result_pins', 'LoopNode.loop_variable_outgoing')
    def test_loop_variable_correspondence_parts_and_internal_targets(self):
        output = self.pin(Uml.OutputPin, type=self.t)
        body = Uml.OpaqueAction(outputValue=[output])
        setup, test = Uml.OpaqueAction(), Uml.OpaqueAction()
        loop = Uml.LoopNode(node=[setup, test, body], setupPart=[setup], test=[test], bodyPart=[body], bodyOutput=[output],
                           loopVariableInput=[self.pin(type=self.t)], loopVariable=[self.pin(Uml.OutputPin, type=self.t)],
                           result=[self.pin(Uml.OutputPin, type=self.t)])
        self.rules(loop, 'LoopNode.result_no_incoming', 'LoopNode.input_edges', 'LoopNode.executable_nodes',
                   'LoopNode.body_output_pins', 'LoopNode.setup_test_and_body', 'LoopNode.matching_output_pins',
                   'LoopNode.matching_loop_variables', 'LoopNode.matching_result_pins', 'LoopNode.loop_variable_outgoing')
        loop.test.append(body)
        self.rules(loop, 'LoopNode.setup_test_and_body', expected=False)
        loop.node.append(Uml.OpaqueAction())
        self.rules(loop, 'LoopNode.executable_nodes', expected=False)
        loop.loopVariable[0].type = Uml.Class()
        self.rules(loop, 'LoopNode.matching_output_pins', 'LoopNode.matching_loop_variables', 'LoopNode.matching_result_pins', expected=False)
        body.outputValue.remove(output)
        self.rules(loop, 'LoopNode.body_output_pins', expected=False)
        Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=loop.result[0])
        self.rules(loop, 'LoopNode.result_no_incoming', expected=False)
        Uml.ObjectFlow(source=loop.loopVariableInput[0], target=Uml.CentralBufferNode())
        self.rules(loop, 'LoopNode.input_edges', expected=False)
        Uml.ObjectFlow(source=loop.loopVariable[0], target=body)
        self.rules(loop, 'LoopNode.loop_variable_outgoing')
        Uml.ObjectFlow(source=loop.loopVariable[0], target=Uml.CentralBufferNode())
        self.rules(loop, 'LoopNode.loop_variable_outgoing', expected=False)

    @verifies('ExpansionNode.region_as_input_or_output', 'InputPin.outgoing_edges_structured_only',
              'OutputPin.incoming_edges_structured_only', 'StructuredActivityNode.output_pin_edges',
              'StructuredActivityNode.input_pin_edges', 'StructuredActivityNode.edges')
    def test_structured_boundary_edges_and_expansion_roles(self):
        inp, out = self.pin(), self.pin(Uml.OutputPin)
        action = Uml.OpaqueAction(inputValue=[self.pin()], outputValue=[self.pin(Uml.OutputPin)])
        structured = Uml.StructuredActivityNode(node=[action], structuredNodeInput=[inp], structuredNodeOutput=[out])
        first = Uml.ObjectFlow(source=inp, target=action.inputValue[0])
        second = Uml.ObjectFlow(source=action.outputValue[0], target=out)
        structured.edge.extend([first, second])
        self.rules(inp, 'InputPin.outgoing_edges_structured_only')
        self.rules(out, 'OutputPin.incoming_edges_structured_only')
        self.rules(structured, 'StructuredActivityNode.input_pin_edges', 'StructuredActivityNode.output_pin_edges', 'StructuredActivityNode.edges')
        structured.edge.remove(second)
        self.rules(structured, 'StructuredActivityNode.edges', expected=False)
        first.target = Uml.CentralBufferNode()
        self.rules(inp, 'InputPin.outgoing_edges_structured_only', expected=False)
        second.source = Uml.CentralBufferNode()
        self.rules(out, 'OutputPin.incoming_edges_structured_only', expected=False)
        Uml.ObjectFlow(source=action.outputValue[0], target=inp)
        Uml.ObjectFlow(source=out, target=action.inputValue[0])
        self.rules(structured, 'StructuredActivityNode.input_pin_edges', 'StructuredActivityNode.output_pin_edges', expected=False)
        expansion = Uml.ExpansionNode()
        self.rules(expansion, 'ExpansionNode.region_as_input_or_output', expected=False)
        region = Uml.ExpansionRegion(inputElement=[expansion])
        self.rules(expansion, 'ExpansionNode.region_as_input_or_output')
        region.outputElement.append(expansion)
        self.rules(expansion, 'ExpansionNode.region_as_input_or_output', expected=False)

    @verifies('CallAction.argument_pins', 'CallAction.result_pins', 'Variable.isAccessibleBy',
              'StructuralFeatureAction.visibility', 'ReadLinkAction.visibility', 'WriteLinkAction.allow_access')
    def test_subtype_variance_and_private_visibility_from_context(self):
        child = Uml.Class(generalization=[Uml.Generalization(general=self.t)])
        behavior = Uml.OpaqueBehavior(ownedParameter=[bounded(Uml.Parameter, 0, 5, type=self.t),
                                                     bounded(Uml.Parameter, type=child, direction=Uml.ParameterDirectionKind.return_)])
        call = Uml.CallBehaviorAction(behavior=behavior, argument=[self.pin(type=child)],
                                      result=[bounded(Uml.OutputPin, 0, 5, type=self.t)])
        self.rules(call, 'CallAction.argument_pins', 'CallAction.result_pins')
        call.argument[0].upperValue.value = 6
        self.rules(call, 'CallAction.argument_pins', expected=False)
        variable = Uml.Variable()
        activity = Uml.Activity(variable=[variable], node=[call])
        self.assertTrue(variable.isAccessibleBy(call))
        self.assertFalse(variable.isAccessibleBy(Uml.OpaqueAction()))
        cls = Uml.Class(ownedBehavior=[activity])
        feature = Uml.Property(visibility=Uml.VisibilityKind.private)
        cls.ownedAttribute.append(feature)
        read = Uml.ReadStructuralFeatureAction(structuralFeature=feature)
        activity.node.append(read)
        self.rules(read, 'StructuralFeatureAction.visibility')
        foreign = Uml.Class(ownedAttribute=[Uml.Property(visibility=Uml.VisibilityKind.private)])
        read.structuralFeature = foreign.ownedAttribute[0]
        self.rules(read, 'StructuralFeatureAction.visibility', expected=False)
        ends = [Uml.Property(type=foreign, visibility=Uml.VisibilityKind.private),
                Uml.Property(type=cls, visibility=Uml.VisibilityKind.private)]
        association = Uml.Association(ownedEnd=ends)
        link = Uml.ReadLinkAction(endData=[Uml.LinkEndData(end=ends[0]), Uml.LinkEndData(end=ends[1], value=self.pin())])
        activity.node.append(link)
        self.rules(link, 'ReadLinkAction.visibility')
        write = Uml.CreateLinkAction(endData=[Uml.LinkEndCreationData(end=e) for e in ends])
        activity.node.append(write)
        self.rules(write, 'WriteLinkAction.allow_access')
        ends[1].type = foreign
        self.rules(link, 'ReadLinkAction.visibility', expected=False)
        self.rules(write, 'WriteLinkAction.allow_access', expected=False)
