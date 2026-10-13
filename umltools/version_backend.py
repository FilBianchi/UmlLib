"""Load the same trusted engine code with independent version-specific module state.

Only bundled Python modules are loaded. Metamodel expressions are never executed.
An isolated package namespace separates relationship maps, instances, transactions,
sessions, native implementations and runtime profile registries.
"""
import importlib.util
from pathlib import Path
import sys
from threading import RLock

_lock=RLock()


def backend_241():
    # Parent umltools is already initialized here. Using Uml241 as the parent
    # would execute its generated facade while the engine is still bootstrapping.
    name='umltools._backend241'
    with _lock:
        if name in sys.modules: return sys.modules[name]
        directory=Path(__file__).parent
        package_spec=importlib.util.spec_from_file_location(name,directory/'__init__.py',
                                      submodule_search_locations=[str(directory)])
        package=importlib.util.module_from_spec(package_spec)
        sys.modules[name]=package
        try:
            spec_name=name+'.specification'
            spec_loader=importlib.util.spec_from_file_location(spec_name,directory/'specification.py')
            specification=importlib.util.module_from_spec(spec_loader)
            sys.modules[spec_name]=specification
            spec_loader.loader.exec_module(specification)
            specification.XMI='{http://www.omg.org/spec/XMI/20100901}'
            specification.SOURCE_NAME='UML-2.4.1.xmi'
            package_spec.loader.exec_module(package)
            package.SEMANTIC_VERSION='2.4.1'
            package.UmlElement.__semantic_version__='2.4.1'
            # The 2.5.1 hand translations are not evidence for 2.4.1 semantics.
            native=sys.modules[name+'.native']
            native.SEMANTIC_VERSION='2.4.1'
            source_constraints=dict(native.CONSTRAINTS)
            source_operations=dict(native.OPERATIONS)
            source_derivations=dict(native.DERIVATIONS)
            common=native.common_structure
            values=native.values
            reviewed_operations={
                'Element.allOwnedElements':common.all_owned_elements,
                'Element.mustBeOwned':common.must_be_owned,
                'Package.mustBeOwned':common.package_must_be_owned,
                'MultiplicityElement.lowerBound':values.lower_bound,
                'MultiplicityElement.upperBound':values.upper_bound,
                'MultiplicityElement.lower':values.lower,
                'MultiplicityElement.upper':values.upper,
                'MultiplicityElement.isMultivalued':values.multivalued,
                'ExtensionEnd.lowerBound':values.extension_lower_bound,
            }
            for classifier in ('LiteralBoolean','LiteralInteger','LiteralReal','LiteralString','LiteralUnlimitedNatural'):
                reviewed_operations[classifier+'.isComputable']=values.computable
            for classifier,operation in [('LiteralBoolean','booleanValue'),('LiteralInteger','integerValue'),
                ('LiteralReal','realValue'),('LiteralString','stringValue'),('LiteralUnlimitedNatural','unlimitedValue')]:
                reviewed_operations[classifier+'.'+operation]=values.literal_value
            for operation in ('booleanValue','integerValue','realValue','stringValue','unlimitedValue'):
                reviewed_operations['ValueSpecification.'+operation]=values.undefined_value
            for operation in ('isComputable','isNull'):
                reviewed_operations['ValueSpecification.'+operation]=values.not_computable
                reviewed_operations['LiteralNull.'+operation]=values.computable
            native.OPERATIONS.clear()
            native.OPERATIONS.update(reviewed_operations)
            native.CONSTRAINTS.clear()
            native.CONSTRAINTS.update({'Element.has_owner':common.has_owner,'Element.not_own_self':common.not_own_self})
            native.DERIVATIONS.clear()
            from .semantics241_common_values import install
            install(package,source_constraints)
            from .semantics241_classifiers import install as install_classifiers
            install_classifiers(package,source_operations,source_constraints,source_derivations)
            from .semantics241_behavior import install as install_behavior
            install_behavior(package,source_operations,source_constraints)
            from .semantics241_activities import install as install_activities
            install_activities(package,source_operations,source_constraints)
            from .semantics241_interactions_rest import install as install_rest
            install_rest(package,source_operations,source_constraints)
            package.AUDIT_REUSE={
                'operations':sorted(k for k,v in native.OPERATIONS.items() if v is source_operations.get(k)),
                'constraints':sorted(k for k,v in native.CONSTRAINTS.items() if v is source_constraints.get(k)),
            }
            for cls in package.REGISTRY.values(): cls.__semantic_version__='2.4.1'
            versions=__import__(name+'.versions',fromlist=['*'])
            versions.SEMANTIC_VERSION='2.4.1'
            exchange=__import__(name+'.xmi',fromlist=['*'])
            exchange.UML_NS='http://www.omg.org/spec/UML/20110701'
            exchange.XMI_NS='http://www.omg.org/spec/XMI/20110701'
            exchange.XMI_VERSION='2.4.1'
            shared_exchange=__import__('umltools.xmi',fromlist=['*'])
            # Exception types carry no backend state; generic callers can catch
            # errors from either isolated reader.
            for exception in ('XmiError','XmiReferenceError','XmiUnsupportedError','XmiVersionError'):
                setattr(exchange,exception,getattr(shared_exchange,exception))
            for module_name in ('static_requirements','stereotypes'):
                module=__import__(name+'.'+module_name,fromlist=['*'])
                def unavailable(*args,**kwargs):
                    raise package.UnsupportedSemanticsError('UML 2.4.1 semantic/exchange contract is not yet audited')
                if module_name=='static_requirements':
                    module.check_static=unavailable
                    module.validate_static=lambda model:[('unsupported version contract','UML2.4.1.prose')]
                elif module_name=='stereotypes':
                    module.apply_profile=unavailable
                    module.apply_stereotype=unavailable
                    module.validate_applications=lambda model:[]
            return package
        except Exception:
            for module_name in list(sys.modules):
                if module_name==name or module_name.startswith(name+'.'): del sys.modules[module_name]
            raise
