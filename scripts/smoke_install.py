"""Run from outside the checkout after installing its distribution."""
import Uml
from umltools import OperationResultError, ModelSession, DeletedElementError
from umltools.native import instances
from umltools.native import check
from umltools.stereotypes import apply_profile, apply_stereotype
from umltools.interaction_mapping import bind_gate_endpoint, mark_extra_global, map_occurrence_gate
from importlib.metadata import version
from importlib.resources import files


model = Uml.Model(name='Installed', packagedElement=[Uml.Class(name='Customer')])
assert model.packagedElement[0].qualifiedName == 'Installed::Customer'
assert len(Uml._classes.__all__) == 255
assert files('umltools.data').joinpath('UML.xmi').is_file()
assert not any(category == 'constraint' for category, _ in model.validate(recursive=True))
parent, target = Uml.Class(), Uml.Class()
child = Uml.Class(generalization=[Uml.Generalization(general=parent)])
channel = Uml.Dependency(client=[parent], supplier=[target])
flow = Uml.InformationFlow(informationSource=[child], informationTarget=[target], realization=[channel])
assert check(flow, 'InformationFlow.must_conform')
formal = Uml.Class()
parameter = Uml.ClassifierTemplateParameter(ownedParameteredElement=formal)
assert formal.isTemplateParameter() and parameter.parameteredElement is formal
try:
    Uml.LiteralReal().realValue()
except OperationResultError:
    pass
else:
    raise AssertionError('Required operation result was not checked')
with ModelSession():
    survivor, deleted = Uml.Class(), Uml.Class(ownedAttribute=[Uml.Property()])
    user = Uml.Property(type=deleted)
    removed = deleted.delete()
    assert len(removed) == 2 and deleted.is_deleted and user.type is None
    assert deleted not in instances(survivor, 'Class')
    try:
        deleted.allParents()
    except DeletedElementError:
        pass
    else:
        raise AssertionError('A tombstone remained queryable')
assert Uml.LiteralUnlimitedNatural().unlimitedValue() == 0
with ModelSession():
    owner, declarations, collaboration = Uml.Class(), Uml.Class(), Uml.Collaboration()
    actual, formal_role = Uml.Property(), Uml.Property()
    owner.ownedAttribute.append(actual)
    declarations.ownedAttribute.append(formal_role)
    collaboration.collaborationRole.append(formal_role)
    use = Uml.CollaborationUse(type=collaboration, roleBinding=[Uml.Dependency(client=[actual], supplier=[formal_role])])
    assert check(use, 'CollaborationUse.client_elements')
    assert check(use, 'CollaborationUse.every_role')
print('Installed UmlLib', version('UmlLib'))
