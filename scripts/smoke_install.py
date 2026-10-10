"""Run from outside the checkout after installing its distribution."""
import Uml
from importlib.metadata import version
from importlib.resources import files


model = Uml.Model(name='Installed', packagedElement=[Uml.Class(name='Customer')])
assert model.packagedElement[0].qualifiedName == 'Installed::Customer'
assert len(Uml._classes.__all__) == 255
assert files('umltools.data').joinpath('UML.xmi').is_file()
assert not any(category == 'constraint' for category, _ in model.validate(recursive=True))
print('Installed UmlLib', version('UmlLib'))
