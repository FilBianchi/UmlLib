"""UML 2.4.1 Interactions, UseCases, Deployments and InformationFlows."""


def install(engine,operations,constraints):
    from importlib import import_module
    n=engine.native;kind=n.kind;required=n.constraints_basic.required;interaction=n.constraints_interactions
    static=import_module(engine.__name__+'.static_requirements')
    def lifeline_classifier(self):
        namespace=required(self.represents).namespace
        context=required(required(self.interaction).context)
        seen=set()
        while namespace is not None:
            if namespace in seen:raise ValueError('Cyclic namespace')
            seen.add(namespace)
            if namespace is context or kind(self,namespace,'Classifier') and namespace in context.allParents():return True
            namespace=namespace.namespace
        return False
    def signature(self):
        if not kind(self,self.signature,'Operation'):return True
        return interaction.reply_signature(self) if self.messageSort is not None and self.messageSort.value=='reply' else interaction.request_signature(self)
    def bounds_apply(self):
        return all(operand.guard is None or operand.guard.minint is None and operand.guard.maxint is None or self.interactionOperator.value=='loop' for operand in self.operand)
    def deployed_components(self):
        return self.deployment is None or all(kind(self,e,'Component') for e in static.deployed_elements(required(self.deployment.location)))
    def messages_cf(self):return interaction.outside_gates(self) and constraints['Gate.inside_cf_matched'](self)
    aliases={'Gate.messages_actual_gate':'Gate.actual_gate_matched',
             'GeneralOrdering.irreflexsive_transitive_closure':'GeneralOrdering.irreflexive_transitive_closure'}
    from . import SPECIFICATIONS as layout
    for name,spec in engine.SPECIFICATIONS.items():
        if layout[name].package not in ('Interactions','UseCases','Deployments','InformationFlows'):continue
        for operation in spec.operations:
            identifier=name+'.'+operation
            if identifier in operations:n.OPERATIONS[identifier]=operations[identifier]
            engine.AUDIT_DECISIONS[identifier]='reviewed shared implementation'
        for rule in spec.constraints:
            identifier=name+'.'+rule
            reference=aliases.get(identifier,identifier)
            if reference in constraints:n.CONSTRAINTS[identifier]=constraints[reference]
    n.CONSTRAINTS.update({
        'CombinedFragment.minint_and_maxint':bounds_apply,
        'Gate.messages_combined_fragment':messages_cf,
        'Message.signature_is_operation':signature,
        'ConsiderIgnoreFragment.type':lambda s:all(kind(s,m,'Operation') or kind(s,m,'Reception') or kind(s,m,'Signal') for m in s.message),
        'Lifeline.same_classifier':lifeline_classifier,
        'Lifeline.selector_specified':lambda s:s.selector is None or required(s.represents).isMultivalued(),
        'DeploymentSpecification.deployed_elements':deployed_components,
    })
    # Gate identification follows Superstructure 2.4.1, printed p.494, including
    # implicit in_/out_ names. Helpers are not new normative operation declarations.
    helpers=engine.UmlElement.__supplemental_operations__
    for identifier,function in operations.items():
        owner,name=identifier.split('.')
        if owner in ('MessageEnd','Gate','Message') and name not in engine.SPECIFICATIONS[owner].operations:helpers[(owner,name)]=function
    n.OPERATIONS['DeploymentTarget.deployedElement']=static.deployed_elements
    engine.AUDIT_DECISIONS['DeploymentTarget.deployedElement']='2.4.1 prose-based Artifact/instance resolution'
