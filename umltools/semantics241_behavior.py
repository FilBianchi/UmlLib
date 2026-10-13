"""UML 2.4.1 CommonBehavior and StateMachines, including old context rules."""


GROUPS=('CommonBehavior','StateMachines')


def install(engine,operations,constraints):
    n=engine.native;kind=n.kind;sm=n.state_machines
    from importlib import import_module
    fact=import_module(engine.__name__+'.semantic_facts').semantic_fact
    def required(value):
        if value is None:raise ValueError('Required UML reference is absent')
        return value
    def context(self):
        machine=required(self.containingStateMachine())
        return machine if machine.context is None or machine.general else machine.context
    def state_context(self,redefined):
        return self.container is not None and redefined.container is not None and self.container.isRedefinitionContextValid(redefined.container)
    def region_context(self,redefined):
        if self.stateMachine is not None:
            return any(redefined in machine.region for machine in self.stateMachine.extendedStateMachine)
        return self.state is not None and self.state.redefinedState is not None and redefined in self.state.redefinedState.region
    def machine_context(self,redefined):return sm.machine_redefinition(self,redefined)
    def extends(candidate,original,attribute):
        seen=set();pending=[candidate]
        while pending:
            current=pending.pop()
            if current is original:return True
            if current in seen:continue
            seen.add(current)
            value=getattr(current,attribute)
            pending.extend(current._items(value))
        return False
    def region_consistent(self,redefinee):
        if not kind(self,redefinee,'Region'):return False
        # extendedRegion preserves inherited vertices/transitions without moving
        # their composite ownership into the extension.
        if extends(redefinee,self,'extendedRegion'):
            vertices=[];transitions=[];current=self;seen=set()
            while current is not None:
                if current in seen:raise ValueError('Cyclic region extension')
                seen.add(current);vertices.extend(current.subvertex);transitions.extend(current.transition)
                current=current.extendedRegion
            return all(v.redefinedState is None or v.redefinedState in vertices for v in redefinee.subvertex if kind(self,v,'State')) and all(t.redefinedTransition is None or t.redefinedTransition in transitions for t in redefinee.transition)
        return all(any(v is old or kind(self,v,'State') and v.redefinedState is old for v in redefinee.subvertex) for old in self.subvertex) and all(any(t is old or t.redefinedTransition is old for t in redefinee.transition) for old in self.transition)
    def regions_preserved(self,redefinee):
        return all(any(region_consistent(r,new) and (new is r or extends(new,r,'extendedRegion')) for new in redefinee.region) for r in self.region)
    def state_consistent(self,redefinee):
        if not kind(self,redefinee,'State'):return False
        if self.submachine is not None:
            return redefinee.submachine is not None and extends(redefinee.submachine,self.submachine,'extendedStateMachine')
        return regions_preserved(self,redefinee)
    def machine_consistent(self,redefinee):
        return kind(self,redefinee,'StateMachine') and (extends(redefinee,self,'extendedStateMachine') or regions_preserved(self,redefinee))
    def transition_consistent(self,redefinee):
        if not redefinee.isRedefinitionContextValid(self):raise ValueError('Invalid redefinition context')
        return kind(self,redefinee,'Transition') and self.source is redefinee.source and list(self.trigger)==list(redefinee.trigger)
    def ancestor(self,s1,s2):return s1 is s2 or s1 in sm.enclosing_states(s2)
    def lca(self,s1,s2):
        first=[s1]+sm.enclosing_states(s1)
        second=[s2]+sm.enclosing_states(s2)
        # The declared return type is Namespace; Region is not a Namespace.
        for state in first:
            if state in second:return state
            if state.container is not None and any(v.container is state.container for v in second):
                return state.container.state or state.container.stateMachine
        raise ValueError('States have no common containing Namespace')
    def must_realize(self):
        if self.specification is None:return True
        classifier=required(self.context)
        return self.specification in classifier.allFeatures() and not any(self.specification in f._items(getattr(f,'redefinedElement',None)) for f in classifier.allFeatures())
    def most_one(self):
        if self.specification is None or not kind(self,self.owner,'Classifier'):return True
        return sum(b.owner is self.owner and b.specification is self.specification for b in n.instances(self,'Behavior'))<=1
    def starting_time(self):
        if not self.isRelative:return True
        triggers=n.reverse(self,'Trigger','event')
        if triggers and all(any(t in transition.trigger for transition in n.instances(self,'Transition')) for t in triggers):return True
        return fact(self,'starting_time_available')
    def signatures(self):
        signatures=[]
        for trigger in self.trigger:
            event=required(trigger.event)
            if kind(self,event,'CallEvent'):signature=[(p.type,p.direction) for p in required(event.operation).ownedParameter]
            elif kind(self,event,'SignalEvent'):signature=[(p.type,'signal') for p in required(event.signal).allAttributes()]
            else:continue
            signatures.append(signature)
        if len(signatures)<=1 or all(s==signatures[0] for s in signatures[1:]):return True
        return not fact(self,'trigger_parameters_assigned')
    def protocols_connected(self):
        for connector in n.instances(self,'Connector'):
            ports=[end.role for end in connector.end if kind(self,end.role,'Port')]
            for consumer in ports:
                requested=[interface.protocol for interface in consumer.required if interface.protocol is not None]
                offered=[interface.protocol for provider in ports if provider is not consumer for interface in provider.provided if interface.protocol is not None]
                for protocol in requested:
                    if protocol is not self:continue
                    if not any(g is protocol or any(c.generalMachine is protocol for c in g.conformance) for g in offered):return False
        return True
    replacements={
        'State.isSimple':sm.simple,'State.redefinitionContext':context,
        'Region.redefinitionContext':context,'Transition.redefinitionContext':context,
        'State.isRedefinitionContextValid':state_context,'Region.isRedefinitionContextValid':region_context,
        'StateMachine.isRedefinitionContextValid':machine_context,
        'State.isConsistentWith':state_consistent,'Region.isConsistentWith':region_consistent,
        'StateMachine.isConsistentWith':machine_consistent,
        'Transition.isConsistentWith':transition_consistent,'StateMachine.ancestor':ancestor,'StateMachine.LCA':lca,
    }
    from . import SPECIFICATIONS as layout
    for name,spec in engine.SPECIFICATIONS.items():
        if layout[name].package not in GROUPS:continue
        for op in spec.operations:
            identifier=name+'.'+op
            function=replacements.get(identifier) or operations.get(identifier)
            if function is not None:n.OPERATIONS[identifier]=function
            engine.AUDIT_DECISIONS[identifier]='2.4.1 implementation' if identifier in replacements else 'reviewed shared implementation'
        for rule in spec.constraints:
            identifier=name+'.'+rule
            if identifier in constraints:n.CONSTRAINTS[identifier]=constraints[identifier]
    n.CONSTRAINTS.update({
        'Behavior.most_one_behaviour':most_one,
        'FunctionBehavior.types_of_parameters':lambda s:all(kind(s,p.type,'DataType') and n.additional_queries.datatype_attributes(s,p.type) for p in s.ownedParameter),
        'Behavior.must_realize':must_realize,'ProtocolStateMachine.ports_connected':protocols_connected,
        'TimeEvent.starting_time':starting_time,'Transition.signatures_compatible':signatures,
    })
    helpers=engine.UmlElement.__supplemental_operations__
    for identifier in ('Behavior.behavioredClassifier','Behavior.inputParameters','Behavior.outputParameters',
                       'BehavioralFeature.inputParameters','BehavioralFeature.outputParameters','FunctionBehavior.hasAllDataTypeAttributes',
                       'Vertex.isContainedInState','Vertex.isContainedInRegion','StateMachine.LCAState'):
        owner,name=identifier.split('.');helpers[(owner,name)]=operations[identifier]
    helpers[('Behavior','behavioredClassifier')]=lambda self,from_:operations['Behavior.behavioredClassifier'](self,**{'from':from_})
