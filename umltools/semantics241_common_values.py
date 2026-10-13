"""Reviewed 2.4.1 CommonStructure/Values translations and package dependencies.

Differences and repairs to malformed published formulas are documented in
UML241_COMMON_VALUES_AUDIT.md. This module only installs explicit declarations.
"""


def install(engine, source_constraints):
    native=engine.native
    common=native.common_structure
    extra=native.additional_queries
    kind=native.kind
    def required(value):
        if value is None: raise ValueError('Required UML reference is absent')
        return value

    def namespaces(self):
        result=[];current=self.namespace
        while current is not None:
            if current in result: raise ValueError('Cyclic namespace chain')
            result.append(current);current=current.namespace
        return result

    def compatible_parameter(self,p): return isinstance(p,type(self))
    def compatible_value(self,p):
        if not isinstance(p,type(self)):return False
        return required(self.type).conformsTo(p.type)

    def lower_bound(self):return 1 if self.lowerValue is None else self.lowerValue.integerValue()
    def upper_bound(self):return 1 if self.upperValue is None else self.upperValue.unlimitedValue()
    def bounds(self):
        low,high=self.lowerBound(),self.upperBound()
        if low is None or high is None:raise ValueError('Undefined multiplicity bound')
        return low,high
    def includes_cardinality(self,C):
        low,high=bounds(self);return low<=C<=high
    def includes_multiplicity(self,M):
        low,high=bounds(self);other_low,other_high=bounds(M)
        return low<=other_low and high>=other_high
    def compatible_multiplicity(self,other):
        low,high=bounds(self);other_low,other_high=bounds(other)
        return low>high or other_low<=low and high<=other_high
    def multivalued(self):
        upper=self.upperBound()
        if upper is None:raise ValueError('Undefined upper bound')
        return upper>1
    def opaque_result(self):
        if self.behavior is None:return None
        results=[p for p in self.behavior.ownedParameter if p.direction is not None and p.direction.value=='return']
        if len(results)!=1:raise ValueError('OpaqueExpression requires exactly one return parameter')
        return results[0]
    def opaque_value(self):
        if not self.isIntegral():raise ValueError('OpaqueExpression must be integral')
        raise native.NativeNotImplemented('Opaque integer value requires an evaluation adapter')

    operations={
        'NamedElement.allNamespaces':namespaces,
        'NamedElement.allOwningPackages':common.all_owning_packages,
        'NamedElement.isDistinguishableFrom':common.distinguishable,
        'NamedElement.namespace':lambda self:self.namespace,
        'NamedElement.qualifiedName':common.qualified_name,
        'NamedElement.separator':common.separator,
        'Namespace.excludeCollisions':common.exclude_collisions,
        'Namespace.getNamesOfMember':common.member_names,
        'Namespace.importMembers':common.import_members,
        'Namespace.importedMember':common.imported_members,
        'Namespace.membersAreDistinguishable':common.distinguishable_members,
        'Namespace.ownedMember':lambda self:list(self.ownedMember),
        'ElementImport.getName':common.import_name,
        'ParameterableElement.isCompatibleWith':compatible_parameter,
        'ParameterableElement.isTemplateParameter':extra.template_parameter,
        'TemplateableElement.isTemplate':common.is_template,
        'TemplateableElement.parameterableElements':common.parameterable_elements,
        'Type.conformsTo':common.type_conforms,
        'MultiplicityElement.lowerBound':lower_bound,
        'MultiplicityElement.upperBound':upper_bound,
        'MultiplicityElement.lower':lambda self:self.lowerBound(),
        'MultiplicityElement.upper':lambda self:self.upperBound(),
        'MultiplicityElement.isMultivalued':multivalued,
        'MultiplicityElement.includesCardinality':includes_cardinality,
        'MultiplicityElement.includesMultiplicity':includes_multiplicity,
        'MultiplicityElement.compatibleWith':compatible_multiplicity,
        'MultiplicityElement.is':lambda self,lowerbound,upperbound:self.lowerBound()==lowerbound and self.upperBound()==upperbound,
        'ValueSpecification.isCompatibleWith':compatible_value,
        'OpaqueExpression.isIntegral':extra.opaque_integral,
        'OpaqueExpression.isNonNegative':extra.opaque_sign,
        'OpaqueExpression.isPositive':extra.opaque_sign,
        'OpaqueExpression.result':opaque_result,
        'OpaqueExpression.value':opaque_value,
        'StringExpression.stringValue':extra.string_expression,
        'Package.allApplicableStereotypes':common.applicable_stereotypes,
        'Package.containingProfile':common.containing_profile,
        'Package.makesVisible':common.makes_visible,
        'Package.visibleMembers':common.visible_members,
        'Package.nestedPackage':common.nested_packages,
        'Package.ownedStereotype':common.owned_stereotypes,
        'Package.ownedType':common.owned_types,
    }
    for identifier,function in operations.items():
        owner,name=identifier.split('.')
        if name not in engine.SPECIFICATIONS[owner].operations:raise RuntimeError('Undeclared query '+identifier)
        native.OPERATIONS[identifier]=function
    reused_constraints=(
        'ElementImport.imported_element_is_public','ElementImport.visibility_public_or_private',
        'PackageImport.public_or_private','Namespace.members_distinguishable',
        'NamedElement.has_qualified_name','NamedElement.has_no_qualified_name',
        'Constraint.boolean_value','Constraint.no_side_effects','Constraint.not_apply_to_self',
        'MultiplicityElement.value_specification_no_side_effects','MultiplicityElement.value_specification_constant',
        'TemplateBinding.parameter_substitution_formal','TemplateBinding.one_parameter_substitution',
        'TemplateParameter.must_be_compatible','TemplateParameterSubstitution.must_be_compatible',
        'TemplateSignature.own_elements','DurationConstraint.first_event_multiplicity',
        'DurationObservation.first_event_multiplicity','OpaqueExpression.language_body_size',
        'OpaqueExpression.one_return_result_parameter','StringExpression.operands','StringExpression.subexpressions',
        'Package.elements_public_or_private',
    )
    for identifier in reused_constraints:native.CONSTRAINTS[identifier]=source_constraints[identifier]
    native.CONSTRAINTS.update({
        'NamedElement.visibility_needs_ownership':lambda self:self.namespace is not None or self.visibility is None,
        'Constraint.value_specification_boolean':lambda self:type(required(self.specification).booleanValue()) is bool,
        'MultiplicityElement.upper_ge_lower':lambda self:self.upperBound() is None or self.lowerBound() is None or self.upperBound()>=self.lowerBound(),
        'MultiplicityElement.lower_ge_0':lambda self:self.lowerBound() is None or self.lowerBound()>=0,
        'OpaqueExpression.only_return_result_parameters':lambda self:self.behavior is None or all(p.direction is not None and p.direction.value=='return' for p in self.behavior.ownedParameter),
    })
    native.DERIVATIONS.update({'NamedElement-qualifiedName':common.qualified_name,
                              'Namespace-member':common.members})
    # Only these old pseudo-body queries have declarative derivations, not OCL bodies.
    engine.SEMANTIC_AUDITS={'CommonStructure/Values':'UML241_COMMON_VALUES_AUDIT.md'}
