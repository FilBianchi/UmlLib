"""Run from outside the checkout after installing its distribution."""
import Uml
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
print('Installed UmlLib', version('UmlLib'))
