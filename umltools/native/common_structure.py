"""Native translations of foundational ownership, names and import semantics."""
from . import query, invariant, derived, unique, kind, instances


@query('Element.allOwnedElements')
def all_owned_elements(self):
    result, pending = [], list(self.ownedElement)
    while pending:
        element = pending.pop(0)
        if element in result: continue
        result.append(element)
        pending.extend(element.ownedElement)
    return result


@query('Element.mustBeOwned')
def must_be_owned(self): return True


@query('Package.mustBeOwned')
def package_must_be_owned(self): return False


@invariant('Element.has_owner')
def has_owner(self): return not self.mustBeOwned() or self.owner is not None


@invariant('Element.not_own_self')
def not_own_self(self): return self not in self.allOwnedElements()


@query('NamedElement.allNamespaces')
def all_namespaces(self):
    result, current, visited = [], self, set()
    while current is not None:
        if id(current) in visited: raise ValueError('Cyclic namespace chain')
        visited.add(id(current))
        owner = current.owner
        if kind(self, owner, 'TemplateParameter'):
            signature = owner.signature
            if signature is None: raise ValueError('Template parameter has no signature')
            enclosing = signature.template
            namespace = enclosing if kind(self, enclosing, 'Namespace') else current.namespace
        else: namespace = current.namespace
        if namespace is None: break
        result.append(namespace)
        current = namespace
    return result


@query('NamedElement.allOwningPackages')
def all_owning_packages(self):
    # The specification follows consecutive enclosing Packages, not all namespaces.
    if not kind(self, self.namespace, 'Package'): return None
    result, current = [], self.namespace
    while kind(self, current, 'Package'):
        result.append(current)
        current = current.namespace
    return result


@query('NamedElement.separator')
def separator(self): return '::'


@query('NamedElement.qualifiedName')
@derived('NamedElement-qualifiedName')
def qualified_name(self):
    namespaces = self.allNamespaces()
    if self.name is None or any(namespace.name is None for namespace in namespaces): return None
    return self.separator().join([namespace.name for namespace in reversed(namespaces)] + [self.name])


@query('NamedElement.clientDependency')
def client_dependency(self): return [dependency for dependency in instances(self, 'Dependency') if self in dependency.client]


@query('NamedElement.isDistinguishableFrom')
def distinguishable(self, n, ns):
    if isinstance(self, type(n)) or isinstance(n, type(self)):
        return not set(ns.getNamesOfMember(self)) & set(ns.getNamesOfMember(n))
    return True


@invariant('NamedElement.visibility_needs_ownership')
def visibility_needs_ownership(self):
    return not (self.namespace is None and self.owner is not None) or self.visibility is None


@invariant('NamedElement.has_qualified_name')
def has_qualified_name(self):
    namespaces = self.allNamespaces()
    if self.name is None or any(ns.name is None for ns in namespaces): return True
    expected = self.separator().join([ns.name for ns in reversed(namespaces)] + [self.name])
    return self.qualifiedName == expected


@invariant('NamedElement.has_no_qualified_name')
def has_no_qualified_name(self):
    return not (self.name is None or any(ns.name is None for ns in self.allNamespaces())) or self.qualifiedName is None


@query('Namespace.excludeCollisions')
def exclude_collisions(self, imps):
    # Interpret "each other" in the specification's prose: exclude the same object.
    return [imp for imp in imps if all(imp is other or imp.isDistinguishableFrom(other, self) for other in imps)]


@query('Namespace.getNamesOfMember')
def member_names(self, element):
    if element in self.ownedMember: return [element.name]
    imports = [item for item in self.elementImport if item.importedElement is element]
    if imports: return unique(item.getName() for item in imports)
    return unique(name for item in self.packageImport if item.importedPackage is not None and element in item.importedPackage.visibleMembers() for name in item.importedPackage.getNamesOfMember(element))


@query('Namespace.importMembers')
def import_members(self, imps):
    return [imp for imp in self.excludeCollisions(imps) if all(imp.isDistinguishableFrom(member, self) for member in self.ownedMember)]


@query('Namespace.importedMember')
def imported_members(self):
    candidates = [item.importedElement for item in self.elementImport if item.importedElement is not None]
    candidates.extend(member for item in self.packageImport if item.importedPackage is not None for member in item.importedPackage.visibleMembers())
    return self.importMembers(unique(candidates))


@derived('Namespace-member')
def members(self):
    result = list(self.ownedMember) + list(self.importedMember)
    if kind(self, self, 'Classifier'): result.extend(self.inheritedMember)
    return unique(result)


@query('Namespace.membersAreDistinguishable')
def distinguishable_members(self):
    members = self.member
    return all(member.isDistinguishableFrom(other, self) for member in members for other in members if member is not other)


@invariant('Namespace.members_distinguishable')
def members_distinguishable(self): return self.membersAreDistinguishable()


@invariant('Namespace.cannot_import_self')
def cannot_import_self(self): return all(item.importedPackage is not self for item in self.packageImport)


@invariant('Namespace.cannot_import_ownedMembers')
def cannot_import_owned(self): return all(item.importedElement not in self.ownedMember for item in self.elementImport)


@query('ElementImport.getName')
def import_name(self):
    if self.alias is not None: return self.alias
    if self.importedElement is None: raise ValueError('ElementImport has no imported element')
    return self.importedElement.name


@invariant('ElementImport.imported_element_is_public')
def imported_is_public(self):
    if self.importedElement is None: raise ValueError('ElementImport has no imported element')
    visibility = self.importedElement.visibility
    return visibility is None or visibility.value == 'public'


@invariant('ElementImport.visibility_public_or_private', 'PackageImport.public_or_private')
def import_visibility(self): return self.visibility is not None and self.visibility.value in ('public', 'private')


@query('Package.nestedPackage')
def nested_packages(self): return [element for element in self.packagedElement if kind(self, element, 'Package')]


@query('Package.ownedType')
def owned_types(self): return [element for element in self.packagedElement if kind(self, element, 'Type')]


@query('Package.ownedStereotype')
def owned_stereotypes(self): return [element for element in self.packagedElement if kind(self, element, 'Stereotype')]


@query('Package.allApplicableStereotypes')
def applicable_stereotypes(self):
    return unique(list(self.ownedStereotype) + [stereotype for package in self.nestedPackage for stereotype in package.allApplicableStereotypes()])


@query('Package.containingProfile')
def containing_profile(self):
    current = self
    while current is not None:
        if kind(self, current, 'Profile'): return current
        current = current.namespace
        if current is not None and not kind(self, current, 'Package'): raise ValueError('Enclosing namespace is not a Package')
    return None


@query('Package.makesVisible')
def makes_visible(self, el):
    if el not in self.member: raise ValueError('makesVisible requires a member of the package')
    # Apply the prose definition; the shipped OCL compares an element to an enum.
    if el.visibility is not None and el.visibility.value != 'public': return False
    if el in self.ownedMember: return True
    if any(item.importedElement is el and item.visibility.value == 'public' for item in self.elementImport): return True
    return any(item.visibility.value == 'public' and el in item.importedPackage.visibleMembers() for item in self.packageImport if item.importedPackage is not None)


@query('Package.visibleMembers')
def visible_members(self): return [member for member in self.member if kind(self, member, 'PackageableElement') and self.makesVisible(member)]


@invariant('Package.elements_public_or_private')
def package_visibility(self): return all(element.visibility is None or element.visibility.value in ('public', 'private') for element in self.packagedElement)


@query('TemplateableElement.isTemplate')
def is_template(self): return self.ownedTemplateSignature is not None


@query('TemplateableElement.parameterableElements')
def parameterable_elements(self): return [element for element in self.allOwnedElements() if kind(self, element, 'ParameterableElement')]


@query('Type.conformsTo')
def type_conforms(self, other): return False
