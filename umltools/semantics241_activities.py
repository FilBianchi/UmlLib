"""UML 2.4.1 Activities/Actions: old equality and at-most node contracts."""


def install(engine,operations,constraints):
    from importlib import import_module
    n=engine.native;kind=n.kind;enum=n.constraints_basic.enum;required=n.constraints_basic.required
    fact=import_module(engine.__name__+'.semantic_facts').semantic_fact
    action=n.activities_actions
    engine.UmlElement.__derived_composite_witnesses__=frozenset(('Activity-structuredNode',))
    def equal_pins(a,b):
        return len(a)==len(b) and all(x.type is y.type and x.isOrdered==y.isOrdered and n.values.lower_bound(x)==n.values.lower_bound(y) and n.values.upper_bound(x)==n.values.upper_bound(y) for x,y in zip(a,b))
    def activity_of(self):return self.containingActivity()
    def parameter_nodes(self):
        activity=required(self.activity);return [v for v in activity.node if kind(self,v,'ActivityParameterNode') and v.parameter is self.parameter]
    def maximum_two(self):
        if enum(required(self.parameter).direction)!='inout':return True
        nodes=parameter_nodes(self)
        return len(nodes)<=2 and sum(bool(p.incoming) for p in nodes)<=1 and sum(bool(p.outgoing) for p in nodes)<=1
    def maximum_one(self):return enum(required(self.parameter).direction)=='inout' or len(parameter_nodes(self))<=1
    def owned(self):return kind(self,self.owner,'Activity') or kind(self,self.owner,'ActivityGroup')
    def structured_owners(self):
        return len([v for v in n.instances(self,'StructuredActivityNode') if self in v._items(v._values.get('node')) or self in v._items(v._values.get('edge'))])<=1
    def autonomous(self):return self.context is None and self.specification is None or not fact(self,'autonomous')
    def ordered_classifier(self):
        if not kind(self,self.unmarshallType,'Classifier'):return False
        declaration=self.unmarshallType.properties().get('ownedAttribute')
        return declaration is not None and declaration.flags.get('isOrdered','false')=='true'
    def index(self):
        feature=getattr(self,'structuralFeature',None) or getattr(self,'variable',None) or getattr(self,'end',None)
        return self.insertAt is None if not required(feature).isOrdered else n.constraints_actions.index_pin(self.insertAt)
    def owner_action(self,expected):return any(kind(self,a,expected) and self in a.endData for a in n.instances(self,'LinkAction'))
    def destruction_index(self):
        end=required(self.end)
        return n.constraints_actions.index_pin(self.destroyAt) if end.isOrdered and not end.isUnique and not self.isDestroyDuplicates else self.destroyAt is None
    def structure_type(self):
        feature=required(self.structuralFeature);type_=required(self.object).type
        if type_ in feature._items(feature.featuringClassifier):return True
        if not kind(self,feature,'Property') or feature.association is None or len(feature.association.memberEnd)!=2:return False
        return any(p is not feature and p.type is type_ for p in feature.association.memberEnd)
    def invocation_receiver(self):
        if self.onPort is None:return True
        receiver=getattr(self,'target',None) or getattr(self,'object',None)
        return receiver is not None and receiver.type is not None and self.onPort in receiver.type.allFeatures()
    def transform(self):
        if self.transformation is None:return True
        inputs,outputs=self.transformation.inputParameters(),self.transformation.outputParameters()
        if len(inputs)!=1 or len(outputs)!=1:return False
        sources=n.constraints_activities.endpoints(self,True);targets=n.constraints_activities.endpoints(self,False)
        return all(required(p.type).conformsTo(inputs[0].type) for p in sources) and all(required(outputs[0].type).conformsTo(p.type) for p in targets) and fact(self.transformation,'pure')
    aliases={
        'ActionInputPin.no_control_or_data_flow':'ActionInputPin.no_control_or_object_flow',
        'ActivityPartition.represents_part_and_is_contained':'ActivityPartition.represents_property_and_is_contained',
        'ActivityPartition.represents_part':'ActivityPartition.represents_property',
        'BroadcastSignalAction.number_and_order':'BroadcastSignalAction.number_of_arguments',
        'ObjectFlow.no_actions':'ObjectFlow.no_executable_nodes',
        'ObjectFlow.selection_behaviour':'ObjectFlow.selection_behavior',
        'RemoveStructuralFeatureValueAction.non_unique_removal':'RemoveStructuralFeatureValueAction.removeAt_and_value',
        'RemoveVariableValueAction.unlimited_natural':'RemoveVariableValueAction.removeAt_and_value',
    }
    from . import SPECIFICATIONS as layout
    for name,spec in engine.SPECIFICATIONS.items():
        if layout[name].package not in ('Activities','Actions'):continue
        for op in spec.operations:
            identifier=name+'.'+op
            function=(lambda self:[node for node in self.node if kind(self,node,'StructuredActivityNode')]) if identifier=='Activity.structuredNode' else operations.get(identifier)
            if function is not None:n.OPERATIONS[identifier]=function
            engine.AUDIT_DECISIONS[identifier]='2.4.1 structural query' if identifier=='Activity.structuredNode' else 'reviewed shared implementation'
        for rule in spec.constraints:
            identifier=name+'.'+rule
            reference=aliases.get(identifier,identifier)
            if reference in constraints:n.CONSTRAINTS[identifier]=constraints[reference]
    n.CONSTRAINTS.update({
        'AcceptEventAction.trigger_events':lambda s:not all(kind(s,t.event,'TimeEvent') for t in s.trigger) or len(s.result)==1,
        'Activity.autonomous':autonomous,
        'Activity.no_supergroups':lambda s:all(g.superGroup is None for g in s.group),
        'Activity.activity_parameter_node':lambda s:all(any(kind(s,node,'ActivityParameterNode') and node.parameter is p for node in s.node) for p in s.ownedParameter),
        'ActivityEdge.owned':owned,'ActivityNode.owned':owned,'ActivityGroup.group_owned':owned,
        'ActivityEdge.structured_node':structured_owners,'ActivityNode.owned_structured_node':structured_owners,
        'ActivityParameterNode.maximum_two_parameter_nodes':maximum_two,'ActivityParameterNode.maximum_one_parameter_node':maximum_one,
        'AddStructuralFeatureValueAction.unlimited_natural_and_multiplicity':index,
        'AddVariableValueAction.single_input_pin':index,'LinkEndCreationData.single_input_pin':index,
        'LinkEndCreationData.create_link_action':lambda s:owner_action(s,'CreateLinkAction'),
        'LinkEndDestructionData.destroy_link_action':lambda s:owner_action(s,'DestroyLinkAction'),
        'LinkEndDestructionData.unlimited_natural_and_multiplicity':destruction_index,
        'CallAction.number_and_order':lambda s:len(s.argument)==len(s.inputParameters()),
        'CallAction.type_ordering_multiplicity':lambda s:equal_pins(s.argument,s.inputParameters()),
        'CallBehaviorAction.argument_pin_equal_parameter':lambda s:len(s.argument)==len(s.inputParameters()),
        'CallBehaviorAction.result_pin_equal_parameter':lambda s:len(s.result)==len(s.outputParameters()),
        'CallBehaviorAction.type_ordering_multiplicity':lambda s:equal_pins(s.argument,s.inputParameters()) and equal_pins(s.result,s.outputParameters()),
        'CallOperationAction.argument_pin_equal_parameter':lambda s:len(s.argument)==len(s.inputParameters()),
        'CallOperationAction.result_pin_equal_parameter':lambda s:len(s.result)==len(s.outputParameters()),
        'CallOperationAction.type_ordering_multiplicity':lambda s:equal_pins(s.argument,s.inputParameters()) and equal_pins(s.result,s.outputParameters()),
        'StartObjectBehaviorAction.number_order_arguments':lambda s:len(s.argument)==len(s.inputParameters()),
        'StartObjectBehaviorAction.number_order_results':lambda s:len(s.result)==len(s.outputParameters()),
        'StartObjectBehaviorAction.type_ordering_multiplicity_match':lambda s:equal_pins(s.argument,s.inputParameters()) and equal_pins(s.result,s.outputParameters()),
        'BroadcastSignalAction.type_ordering_multiplicity':lambda s:equal_pins(s.argument,required(s.signal).allAttributes()),
        'SendSignalAction.type_ordering_multiplicity':lambda s:equal_pins(s.argument,required(s.signal).allAttributes()),
        'ExceptionHandler.exception_body':lambda s:not required(s.handlerBody).incoming and not s.handlerBody.outgoing and not required(s.exceptionInput).incoming and not s.exceptionInput.outgoing,
        'ExceptionHandler.result_pins':lambda s:not kind(s,s.protectedNode,'StructuredActivityNode') or not s.protectedNode.output or kind(s,s.handlerBody,'StructuredActivityNode') and len(s.handlerBody.output)==len(s.protectedNode.output) and all(a.type is b.type for a,b in zip(s.handlerBody.output,s.protectedNode.output)),
        'ExpansionRegion.expansion_nodes':lambda s:bool(s.inputElement),
        'InvocationAction.on_port_receiver':invocation_receiver,
        'ObjectFlow.transformation_behaviour':transform,
        'StructuralFeatureAction.same_type':structure_type,
        'WriteStructuralFeatureAction.input_pin':lambda s:s.value is None or s.value.type is required(s.structuralFeature).type,
        'WriteStructuralFeatureAction.multiplicity':lambda s:n.constraints_actions.one(s.value),
        'WriteVariableAction.same_type':lambda s:s.value is None or s.value.type is required(s.variable).type,
        'UnmarshallAction.type_and_ordering':lambda s:len(s.result)==len(required(s.unmarshallType).allAttributes()) and all(a.type is b.type and a.isOrdered==b.isOrdered for a,b in zip(s.result,s.unmarshallType.allAttributes())),
        'UnmarshallAction.multiplicity_of_result':lambda s:len(s.result)==len(required(s.unmarshallType).allAttributes()) and all(a.compatibleWith(b) for a,b in zip(s.result,s.unmarshallType.allAttributes())),
        'UnmarshallAction.same_type':lambda s:required(s.object).type is s.unmarshallType,
        'UnmarshallAction.unmarshallType_is_classifier':ordered_classifier,
        'Variable.owned':lambda s:(s.scope is not None)!=(s.activityScope is not None),
    })
    helpers=engine.UmlElement.__supplemental_operations__
    owners=('Action','ActivityGroup','ActivityNode','StructuredActivityNode','CallAction','CallBehaviorAction','CallOperationAction',
            'LoopNode','ConditionalNode','LinkEndData','LinkEndCreationData','LinkEndDestructionData','ReadLinkAction','StartObjectBehaviorAction')
    for identifier,function in operations.items():
        owner,name=identifier.split('.')
        if owner in owners and name not in engine.SPECIFICATIONS[owner].operations:helpers[(owner,name)]=function
