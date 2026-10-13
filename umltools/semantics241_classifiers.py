"""2.4.1 Classification, SimpleClassifiers, Packages and StructuredClassifiers.

Public declared signatures stay 2.4.1. Additive helpers are implementation
queries, not added normative declarations. Version decisions are inventoried.
"""
GROUPS=('Classification','SimpleClassifiers','Packages','StructuredClassifiers')


def install(engine,operations,constraints,derivations):
    native=engine.native;kind=native.kind;unique=native.unique
    classifier=native.classification;structured=native.structured_classifiers;extra=native.additional_queries
    def required(value):
        if value is None:raise ValueError('Required UML reference is absent')
        return value
    def default_text(self):
        value=self.defaultValue
        if value is None:return None
        if kind(self,value,'LiteralString'):return value.stringValue()
        if kind(self,value,'LiteralBoolean'):return 'true' if value.booleanValue() else 'false'
        if kind(self,value,'LiteralInteger') or kind(self,value,'LiteralReal'):return str(value.value)
        if kind(self,value,'LiteralUnlimitedNatural'):return '*' if value.value==float('inf') else str(value.value)
        if kind(self,value,'LiteralNull'):return 'null'
        raise native.NativeNotImplemented('Legacy default text requires a language representation adapter')
    def property_opposite(self):
        if self.owningAssociation is not None or self.association is None or len(self.association.memberEnd)!=2:return None
        other=next((p for p in self.association.memberEnd if p is not self),None)
        return other if other is not None and other.owningAssociation is None else None
    def property_compatible(self,p):
        return isinstance(p,type(self)) and required(self.type).conformsTo(p.type)
    def property_consistent(self,redefinee):
        if not redefinee.isRedefinitionContextValid(self):raise ValueError('Invalid redefinition context')
        if not kind(self,redefinee,'Property'):return False
        old_low,new_low=self.lowerBound(),redefinee.lowerBound()
        old_high,new_high=self.upperBound(),redefinee.upperBound()
        return required(redefinee.type).conformsTo(self.type) and (old_low is None or new_low is None or new_low>=old_low) and (old_high is None or new_high is None or new_high<=old_high) and (not self.isComposite or redefinee.isComposite)
    def operation_consistent(self,redefinee):
        if not redefinee.isRedefinitionContextValid(self):raise ValueError('Invalid redefinition context')
        return kind(self,redefinee,'Operation') and len(self.ownedParameter)==len(redefinee.ownedParameter) and all(required(new.type).conformsTo(old.type) for old,new in zip(self.ownedParameter,redefinee.ownedParameter))
    def behavior_distinguishable(self,n,ns):
        if not kind(self,n,'BehavioralFeature') or not set(ns.getNamesOfMember(self))&set(ns.getNamesOfMember(n)):return True
        return [p.type for p in self.ownedParameter]!=[p.type for p in n.ownedParameter]
    def realized(self,classifier_):return classifier.realized_interfaces(classifier_)
    def used(self,classifier_):return classifier.used_interfaces(classifier_)
    def interfaces(self,provided):
        classifiers=[self]+self.allParents()
        realizers=unique(c for c0 in classifiers for r in getattr(c0,'realization',[]) for c in r.realizingClassifier)
        realizers=unique(realizers+[p for c in realizers for p in c.allParents()])
        query=classifier.all_realized_interfaces if provided else classifier.all_used_interfaces
        port='provided' if provided else 'required'
        return unique([i for c in classifiers+realizers for i in query(c)]+[i for c in classifiers for p in getattr(c,'ownedPort',[]) for i in getattr(p,port)])
    def port_interfaces(self,provided):
        type_=required(self.type)
        if self.isConjugated:provided=not provided
        if provided and kind(self,type_,'Interface'):return [type_]
        return classifier.all_realized_interfaces(type_) if provided else classifier.all_used_interfaces(type_)
    def role_interfaces(self,end,provided):
        role=required(end.role)
        if kind(self,role,'Port'):
            if self.kind.value=='delegation' and end.partWithPort is None and not role.isBehavior:provided=not provided
            return list(role.provided if provided else role.required)
        type_=required(role.type)
        if provided and kind(self,type_,'Interface'):return [type_]
        return classifier.all_realized_interfaces(type_) if provided else classifier.all_used_interfaces(type_)
    def compatible_features(self,provided,requested):
        if provided is requested:return True
        if provided.name!=requested.name or not isinstance(provided,type(requested)):return False
        if kind(self,provided,'BehavioralFeature'):
            if len(provided.ownedParameter)!=len(requested.ownedParameter):return False
            return all(a.direction==b.direction and required(a.type).conformsTo(b.type) for a,b in zip(provided.ownedParameter,requested.ownedParameter))
        if kind(self,provided,'TypedElement'):return required(provided.type).conformsTo(requested.type)
        return True
    def interface_contract(self):
        for end in self.end:
            others=[other for other in self.end if other is not end]
            supplied=[f for other in others for interface in role_interfaces(self,other,True) for f in interface.allFeatures()]
            for interface in role_interfaces(self,end,False):
                if any(not any(compatible_features(self,p,r) for p in supplied) for r in interface.allFeatures()):return False
        return True
    def compatible_connector(self):
        if any(kind(self,e.role,'Port') for e in self.end):return interface_contract(self)
        types=[required(required(e.role).type) for e in self.end]
        return all(a.conformsTo(b) or b.conformsTo(a) for a in types for b in types)
    def connector_multiplicities(self):
        for connector in self.ownedConnector:
            for end in connector.end:
                if not required(end.role).compatibleWith(end):return False
                if end.definingEnd is not None and not end.compatibleWith(end.definingEnd):return False
        return True
    def port_destroyed(self):
        raise native.NativeNotImplemented('Port destruction is enforced by delete(); it is an event obligation, not a static predicate')
    replacements={
        'Classifier.inherit':lambda self,inhs:list(inhs),
        'Class.inherit':classifier.inherit,'DataType.inherit':classifier.inherit,
        'Property.default':default_text,'Parameter.default':default_text,
        'Property.isAttribute':lambda self,p:classifier.property_classifier(p) is not None,
        'Property.isCompatibleWith':property_compatible,'Property.isConsistentWith':property_consistent,
        'Property.opposite':property_opposite,'Operation.isConsistentWith':operation_consistent,
        'BehavioralFeature.isDistinguishableFrom':behavior_distinguishable,
        'RedefinableElement.isConsistentWith':lambda self,redefinee:classifier.consistent(self,redefinee),
        'RedefinableElement.isRedefinitionContextValid':lambda self,redefined:classifier.redefinition_context(self,redefined),
        'RedefinableTemplateSignature.isConsistentWith':lambda self,redefinee:extra.template_consistency(self,redefinee),
        'Component.realizedInterfaces':lambda self,**args:realized(self,args['classifier']),
        'Component.usedInterfaces':lambda self,**args:used(self,args['classifier']),
        'Component.provided':lambda self:interfaces(self,True),'Component.required':lambda self:interfaces(self,False),
        'Port.provided':lambda self:port_interfaces(self,True),'Port.required':lambda self:port_interfaces(self,False),
        'Association.endType':classifier.end_types,
    }
    # Groups are the stable API facades used by the generator. Read the same
    # 2.5.1 class-package mapping without changing either version's specifications.
    from . import SPECIFICATIONS as layout
    names=[name for name,spec in layout.items() if spec.package in GROUPS]
    decisions={}
    for name in names:
        spec=engine.SPECIFICATIONS[name]
        for operation in spec.operations:
            identifier=name+'.'+operation
            function=replacements.get(identifier) or operations.get(identifier)
            if function is not None:
                native.OPERATIONS[identifier]=function
                decisions[identifier]='2.4.1 implementation' if identifier in replacements else 'reviewed shared implementation'
        for rule in spec.constraints:
            identifier=name+'.'+rule
            if identifier in constraints:native.CONSTRAINTS[identifier]=constraints[identifier]
        for prop in spec.properties.values():
            if prop.id in derivations:native.DERIVATIONS[prop.id]=derivations[prop.id]
    native.CONSTRAINTS.update({
        'Class.passive_class':lambda self:self.isActive or not self.ownedReception,
        'Reception.not_query':lambda self:True, # Reception has no isQuery slot.
        'Association.binary_associations':lambda self:not any(p.aggregation.value!='none' for p in self.memberEnd) or len(self.memberEnd)==2,
        'Property.binding_to_attribute':lambda self:not self.isAttribute(self) or all(kind(self,t.formal.parameteredElement,'Property') and self.isAttribute(t.formal.parameteredElement) for t in native.reverse(self,'TemplateParameterSubstitution','actual')),
        'Property.multiplicity_of_composite':lambda self:not self.isComposite or self.upperBound() is None or self.upperBound()<=1,
        'Property.subsetting_rules':lambda self:all(required(self.type).conformsTo(p.type) and (self.upperBound() is None or p.upperBound() is None or self.upperBound()<=p.upperBound()) for p in self.subsettedProperty),
        'EnumerationLiteral.classifier_equals_owning_enumeration':lambda self:self.classifier is self.enumeration,
        'RedefinableTemplateSignature.inherited_parameters':lambda self:set(self.inheritedParameter)==set(p for s in self.extendedSignature for p in s.parameter),
        'Generalization.generalization_same_classifier':lambda self:all(required(self.general) is g.general for s in self.generalizationSet for g in s.generalization),
        'Connector.between_interfaces_ports':interface_contract,
        'Connector.compatible':compatible_connector,
        'StructuredClassifier.multiplicities':connector_multiplicities,
        'Port.port_destroyed':port_destroyed,
        # In 2.4.1 Property.opposite deliberately excludes association-owned
        # ends; this ownership rule still refers to the other association end.
        'Stereotype.associationEndOwnership':lambda self:all(any(other is not p and other.owner is p.association for other in p.association.memberEnd) for p in self.ownedAttribute if p.association is not None and not kind(self,p.association,'Extension') and not kind(self,p.type,'Stereotype')),
    })
    native.DERIVATIONS['Feature-featuringClassifier']=lambda self:[c for c in native.instances(self,'Classifier') if self in c.feature]
    native.DERIVATIONS['ExtensionEnd-lower']=lambda self:self.lowerBound()
    helpers={}
    for identifier in ('Classifier.allAttributes','Classifier.allSlottableFeatures','Classifier.allRealizedInterfaces',
                       'Classifier.allUsedInterfaces','Classifier.directlyRealizedInterfaces','Classifier.directlyUsedInterfaces','StructuredClassifier.allRoles'):
        owner,name=identifier.split('.');helpers[(owner,name)]=operations[identifier]
    engine.UmlElement.__supplemental_operations__=helpers
    engine.AUDIT_DECISIONS=decisions
