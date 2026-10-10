"""Value, template, deployment, profile and behavioral feature queries."""
from . import query, kind, unique


@query('OpaqueExpression.isIntegral')
def opaque_integral(self): return False


@query('OpaqueExpression.isNonNegative', 'OpaqueExpression.isPositive')
def opaque_sign(self):
    if not self.isIntegral(): raise ValueError('OpaqueExpression must be integral')
    return False


@query('OpaqueExpression.value')
def opaque_value(self):
    if not self.isIntegral(): raise ValueError('OpaqueExpression must be integral')
    return 0


@query('OpaqueExpression.result')
def opaque_result(self):
    if self.behavior is None: return None
    if not self.behavior.ownedParameter: raise ValueError('Expression behavior has no result parameter')
    return self.behavior.ownedParameter[0]


@query('StringExpression.stringValue')
def string_expression(self):
    parts = self.subExpression or self.operand
    values = [part.stringValue() for part in parts]
    if any(value is None for value in values): raise ValueError('StringExpression has a non-string operand')
    return ''.join(values)


@query('UseCase.allIncludedUseCases')
def included_cases(self):
    result, pending = [], [inc.addition for inc in self.include]
    while pending:
        case = pending.pop(0)
        if case is None: raise ValueError('Include requires an addition use case')
        if case in result: continue
        result.append(case)
        pending.extend(inc.addition for inc in case.include)
    return result


@query('EnumerationLiteral.classifier')
def literal_classifier(self): return self.enumeration


@query('Extension.isRequired')
def extension_required(self):
    ends = self._items(self.ownedEnd)
    if len(ends) != 1: raise ValueError('Extension requires exactly one owned end')
    return ends[0].lowerBound() == 1


@query('Extension.metaclassEnd')
def metaclass_end(self):
    ends = [end for end in self.memberEnd if end not in self._items(self.ownedEnd)]
    if len(ends) != 1: raise ValueError('Extension requires exactly one metaclass end')
    return ends[0]


@query('Extension.metaclass')
def metaclass(self):
    type_ = self.metaclassEnd().type
    if not kind(self, type_, 'Class'): raise ValueError('Extension metaclass end must be typed by a Class')
    return type_


@query('Stereotype.containingProfile', 'Stereotype.profile')
def stereotype_profile(self):
    if not kind(self, self.namespace, 'Package'): raise ValueError('Stereotype must belong to a package')
    return self.namespace.containingProfile()


@query('DeploymentTarget.deployedElement')
def deployed(self):
    return unique(m.utilizedElement for deployment in self.deployment for artifact in deployment.deployedArtifact if kind(self, artifact, 'Artifact') for m in artifact.manifestation if m.utilizedElement is not None)


@query('ParameterableElement.isCompatibleWith')
def compatible(self, p): return isinstance(self, type(p))


@query('ParameterableElement.isTemplateParameter')
def template_parameter(self): return self.templateParameter is not None


@query('FunctionBehavior.hasAllDataTypeAttributes')
def datatype_attributes(self, d):
    visited, pending = set(), [d]
    while pending:
        current = pending.pop()
        if current in visited: continue
        visited.add(current)
        for attribute in current.ownedAttribute:
            if not kind(self, attribute.type, 'DataType'): return False
            pending.append(attribute.type)
    return True


@query('BehavioralFeature.isDistinguishableFrom')
def feature_distinguishable(self, n, ns):
    if not kind(self, n, 'BehavioralFeature') or not set(ns.getNamesOfMember(self)) & set(ns.getNamesOfMember(n)): return True
    if self is n: return True
    def signature(feature):
        fields = ('name', 'type', 'effect', 'direction', 'isException', 'isStream', 'isOrdered', 'isUnique', 'lower', 'upper')
        return [tuple(getattr(p, field) for field in fields) for p in feature.ownedParameter]
    return signature(self) != signature(n)


@query('BehavioralFeature.inputParameters')
def feature_inputs(self): return [p for p in self.ownedParameter if p.direction.value in ('in', 'inout')]


@query('BehavioralFeature.outputParameters')
def feature_outputs(self): return [p for p in self.ownedParameter if p.direction.value in ('out', 'inout', 'return')]


@query('Parameter.default')
def parameter_default(self):
    if kind(self, self.type, 'PrimitiveType') and self.type.name == 'String':
        return None if self.defaultValue is None else self.defaultValue.stringValue()
    return None


@query('RedefinableTemplateSignature.inheritedParameter')
def inherited_parameters(self): return unique(p for signature in self._items(self.extendedSignature) for p in signature.parameter)


@query('RedefinableTemplateSignature.isConsistentWith')
def template_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return kind(self, redefiningElement, 'RedefinableTemplateSignature')
