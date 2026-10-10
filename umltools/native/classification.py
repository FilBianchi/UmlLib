"""Python translations of classifier inheritance and redefinition queries."""
from . import query, invariant, unique, kind, instances


@query('Classifier.parents')
def parents(self):
    if any(generalization.general is None for generalization in self.generalization): raise ValueError('Generalization has no general classifier')
    return unique(generalization.general for generalization in self.generalization)


@query('Classifier.allParents')
def all_parents(self):
    result, pending = [], list(self.parents())
    while pending:
        parent = pending.pop(0)
        if parent in result: continue
        result.append(parent)
        pending.extend(parent.parents())
    return result


@query('Classifier.general')
def general(self): return self.parents()


@query('Classifier.conformsTo')
def conforms(self, other): return kind(self, other, 'Classifier') and (self is other or other in self.allParents())


@query('Classifier.maySpecializeType')
def may_specialize(self, c): return isinstance(self, type(c))


@query('Classifier.isTemplate')
def is_template(self): return self.ownedTemplateSignature is not None or any(parent.isTemplate() for parent in self.parents())


@query('Classifier.hasVisibilityOf')
def has_visibility(self, n):
    candidates = unique(list(self.ownedMember) + list(self.importedMember) + [member for parent in self.allParents() for member in parent.member])
    if n not in candidates: raise ValueError('hasVisibilityOf requires a member of this classifier or an ancestor')
    return n.visibility is None or n.visibility.value != 'private'


@query('Classifier.inheritableMembers')
def inheritable_members(self, c):
    if self not in c.allParents(): raise ValueError('inheritableMembers requires a descendant classifier')
    return [member for member in self.member if c.hasVisibilityOf(member)]


@query('Classifier.inherit')
def inherit(self, inhs):
    redefinitions = [member for member in self.ownedMember if kind(self, member, 'RedefinableElement')]
    return [member for member in inhs if not (kind(self, member, 'RedefinableElement') and any(member in redefining.redefinedElement for redefining in redefinitions))]


@query('Classifier.inheritedMember')
def inherited_members(self): return self.inherit(unique(member for parent in self.parents() for member in parent.inheritableMembers(self)))


@query('Classifier.allFeatures')
def all_features(self): return [member for member in self.member if kind(self, member, 'Feature')]


@query('Classifier.allAttributes')
def all_attributes(self):
    candidates = unique(list(self.attribute) + [attribute for parent in self.parents() for attribute in parent.allAttributes()])
    members = self.member
    return [attribute for attribute in candidates if attribute in members]


@query('Classifier.allSlottableFeatures')
def slottable_features(self):
    inherited = self.inherit(unique(attribute for parent in self.allParents() for attribute in parent.attribute))
    return unique([member for member in self.member if kind(self, member, 'StructuralFeature')] + inherited)


@query('Classifier.directlyRealizedInterfaces')
def realized_interfaces(self):
    return unique(interface for dependency in self.clientDependency if kind(self, dependency, 'Realization') and all(kind(self, supplier, 'Interface') for supplier in dependency.supplier) for interface in dependency.supplier)


@query('Classifier.directlyUsedInterfaces')
def used_interfaces(self):
    dependencies = [dependency for dependency in instances(self, 'Usage') if self in dependency.client]
    return unique(interface for dependency in dependencies if all(kind(self, supplier, 'Interface') for supplier in dependency.supplier) for interface in dependency.supplier)


@query('Classifier.allRealizedInterfaces')
def all_realized_interfaces(self): return unique(self.directlyRealizedInterfaces() + [interface for parent in self.allParents() for interface in parent.directlyRealizedInterfaces()])


@query('Classifier.allUsedInterfaces')
def all_used_interfaces(self): return unique(self.directlyUsedInterfaces() + [interface for parent in self.allParents() for interface in parent.directlyUsedInterfaces()])


@query('Classifier.isSubstitutableFor')
def substitutable(self, contract): return any(substitution.contract is contract for substitution in self.substitution)


@invariant('Classifier.specialize_type')
def specialize_type(self): return all(self.maySpecializeType(parent) for parent in self.parents())


@invariant('Classifier.non_final_parents')
def non_final_parents(self): return all(not parent.isFinalSpecialization for parent in self.parents())


@invariant('Classifier.no_cycles_in_generalization')
def no_cycles(self): return self not in self.allParents()


@invariant('Classifier.maps_to_generalization_set')
def maps_to_generalization_set(self):
    for group in self.powertypeExtent:
        for generalization in group.generalization:
            if generalization.general is None or generalization.specific is None: raise ValueError('Incomplete generalization')
            if generalization.general is self or self in generalization.general.allParents() or generalization.specific is self or generalization.specific in self.allParents(): return False
    return True


@query('RedefinableElement.isRedefinitionContextValid')
def redefinition_context(self, redefinedElement):
    return any(all(parent in context.allParents() for parent in self._items(redefinedElement.redefinitionContext)) for context in self._items(self.redefinitionContext))


@query('RedefinableElement.isConsistentWith')
def consistent(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return False


@invariant('RedefinableElement.redefinition_consistent')
def redefinition_consistent(self): return all(element.isConsistentWith(self) for element in self.redefinedElement)


@invariant('RedefinableElement.non_leaf_redefinition')
def non_leaf(self): return all(not element.isLeaf for element in self.redefinedElement)


@invariant('RedefinableElement.redefinition_context_valid')
def redefinition_context_valid(self): return all(self.isRedefinitionContextValid(element) for element in self.redefinedElement)


@query('Association.endType')
def end_types(self): return unique(end.type for end in self.memberEnd)


@invariant('Association.specialized_end_number')
def end_number(self): return all(len(parent.memberEnd) == len(self.memberEnd) for parent in self.parents() if kind(self, parent, 'Association'))


@invariant('Association.specialized_end_types')
def end_type_conformance(self):
    for parent in self.parents():
        if not kind(self, parent, 'Association'): continue
        if len(parent.memberEnd) != len(self.memberEnd): return False
        for end, parent_end in zip(self.memberEnd, parent.memberEnd):
            if end.type is None: raise ValueError('Untyped association end')
            if not end.type.conformsTo(parent_end.type): return False
    return True


@invariant('Association.binary_associations')
def binary_associations(self):
    aggregated = any(end.aggregation.value != 'none' for end in self.memberEnd)
    return not aggregated or (len(self.memberEnd) == 2 and any(end.aggregation.value == 'none' for end in self.memberEnd))


@invariant('Association.association_ends')
def owned_ends(self): return len(self.memberEnd) <= 2 or all(end in self.ownedEnd for end in self.memberEnd)


@invariant('Association.ends_must_be_typed')
def typed_ends(self): return all(end.type is not None for end in self.memberEnd)


@query('Class.superClass')
def super_classes(self): return [parent for parent in self.parents() if kind(self, parent, 'Class')]


@query('Class.extension')
def extensions(self):
    result = []
    for extension in instances(self, 'Extension'):
        types = [end.type for end in extension.memberEnd]
        if any(not kind(self, type_, 'Classifier') for type_ in types): raise ValueError('Extension end is not typed by a classifier')
        if self in types or any(self in type_.allParents() for type_ in types): result.append(extension)
    return result


@query('StructuredClassifier.part')
def parts(self): return [attribute for attribute in self.ownedAttribute if attribute.isComposite]


@query('StructuredClassifier.allRoles')
def roles(self): return [feature for feature in self.allFeatures() if kind(self, feature, 'ConnectableElement')]


@query('EncapsulatedClassifier.ownedPort')
def owned_ports(self): return [attribute for attribute in self.ownedAttribute if kind(self, attribute, 'Port')]


@query('Property.isComposite')
def composite_property(self): return self.aggregation.value == 'composite'


def property_classifier(self):
    if kind(self, self.owner, 'Classifier') and self in self.owner.attribute: return self.owner
    return next((classifier for classifier in instances(self, 'Classifier') if self in classifier.attribute), None)


@query('Property.isAttribute')
def attribute(self): return property_classifier(self) is not None


@query('Property.isNavigable')
def navigable(self): return property_classifier(self) is not None or self.association is not None and self in self.association.navigableOwnedEnd


@query('Property.opposite')
def opposite(self):
    if self.association is None or len(self.association.memberEnd) != 2: return None
    return next((end for end in self.association.memberEnd if end is not self), None)


@query('Property.subsettingContext')
def subsetting_context(self):
    if self.association is not None: return unique(end.type for end in self.association.memberEnd if end is not self)
    classifier = property_classifier(self)
    return [] if classifier is None else [classifier]


@query('Property.isCompatibleWith')
def property_compatible(self, p):
    # The XMI says TypeElement in one place; the UML metaclass is TypedElement.
    if not isinstance(self, type(p)): return False
    if kind(self, p, 'TypedElement'):
        if self.type is None: raise ValueError('Property has no type')
        return self.type.conformsTo(p.type)
    return True


@query('Property.isConsistentWith')
def property_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    if not kind(self, redefiningElement, 'Property'): return False
    prop = redefiningElement
    if prop.type is None: raise ValueError('Redefining property has no type')
    # The shipped upper-bound clause mistakenly repeats lowerBound; use upperBound.
    return prop.type.conformsTo(self.type) and prop.lowerBound() >= self.lowerBound() and prop.upperBound() <= self.upperBound() and (not self.isComposite or prop.isComposite)


@query('Operation.returnResult')
def return_parameters(self): return [parameter for parameter in self.ownedParameter if parameter.direction.value == 'return']


@query('Operation.isOrdered')
def ordered_result(self): return any(parameter.isOrdered for parameter in self.returnResult())


@query('Operation.isUnique')
def unique_result(self):
    parameters = self.returnResult()
    return not parameters or any(parameter.isUnique for parameter in parameters)


@query('Operation.lower')
def lower_result(self):
    parameters = self.returnResult()
    return parameters[0].lower if parameters else None


@query('Operation.upper')
def upper_result(self):
    parameters = self.returnResult()
    return parameters[0].upper if parameters else None


@query('Operation.type')
def result_type(self):
    parameters = self.returnResult()
    return parameters[0].type if parameters else None


@query('Operation.isConsistentWith')
def operation_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    if not kind(self, redefiningElement, 'Operation'): return False
    if len(self.ownedParameter) != len(redefiningElement.ownedParameter): return False
    for original, replacement in zip(self.ownedParameter, redefiningElement.ownedParameter):
        if (original.isUnique, original.isOrdered, original.direction) != (replacement.isUnique, replacement.isOrdered, replacement.direction): return False
        if original.type is None or replacement.type is None: raise ValueError('Operation parameter has no type')
        if not (replacement.type.conformsTo(original.type) or original.type.conformsTo(replacement.type)): return False
        direction = replacement.direction.value
        if direction in ('in', 'inout') and not original.compatibleWith(replacement): return False
        if direction in ('out', 'inout', 'return') and not replacement.compatibleWith(original): return False
    return True
