# Profili runtime UML 2.4.1 — 0.19.0

Le applicazioni dei profili e degli stereotipi usano i registri isolati 2.4.1.
Le definizioni Profile/Stereotype restano oggetti UML; StereotypeApplication e
ProfileObject sono le rispettive istanze runtime, distinte da InstanceSpecification.

```python
from Uml241.stereotypes import apply_profile, apply_stereotype, unapply_profile
from Uml241.xmi import dump, load

# model, element, profile e stereotype sono definizioni/oggetti Uml241.
# profile contiene una Extension valida verso la metaclasse dell'elemento.
apply_profile(model, profile)
application = apply_stereotype(element, stereotype, values={'label': 'Entity'})
application.set_value('label', 'Updated')
print(application.tagged_values, application.validate())
dump(model, 'profiled.xmi')
restored = load('profiled.xmi')
unapply_profile(model, profile)
```

## Contratti implementati

- Applicazione/rimozione dei profili, disponibilità per ownership e import,
  estensioni richieste e loro sottotipi concreti, esclusione delle applicazioni duplicate.
- Un solo legame base per applicazione, selezione esplicita quando più metaclassi
  sono compatibili, rebind atomico e conservazione dei valori.
- Tag Boolean/Integer/Real/String/UnlimitedNatural, enum del modello, riferimenti
  a metaclassi e istanze di Class/DataType definite nel profilo.
- Limiti di molteplicità, ordine, unicità e bag; default literal, readonly, proprietà
  ereditate/ridefinite, DataType immutabili e modifica multipla atomica.
- Associazioni binarie navigabili tra valori, composizione e cicli, cancellazione
  e cleanup dei riferimenti quando vengono eliminati basi, definizioni o profili.
- Viste isStrict e creazione controllata dei soli tipi disponibili, senza cancellare
  gli elementi UML esistenti nascosti dalla vista.
- Vincoli utente Boolean literal o callback Python fidate; gli OCL opachi restano
  testo e richiedono un evaluator esplicito. Le callback non possono modificare il
  modello durante la validazione e non vengono serializzate.

I tipi PrimitiveType personalizzati conservano identità e valore lessicale:

```python
from Uml241.primitive_values import PrimitiveValue, register_primitive_codec
from decimal import Decimal

register_primitive_codec(money_type, decode=Decimal, encode=str,
    validate=lambda value: isinstance(value, Decimal) and value >= 0)
application.set_value('price', PrimitiveValue.from_python(money_type, Decimal('12.30')))
```

Il codec si applica alla precisa definizione money_type, non ad alias Ecore o nomi
di dominio. XMI conserva definizione e testo; dopo l'import occorre registrare di
nuovo le callback. Un valore senza semantica conosciuta rimane accessibile, ma la
validazione segnala unsupported anziché inventare un risultato positivo.

## Differenze normative e interpretazioni

Riferimento: [UML 2.4.1 Superstructure](https://www.omg.org/spec/UML/2.4.1/Superstructure/PDF),
18.3.2 Extension (pp.664–665), 18.3.5 Profile, 18.3.6 ProfileApplication (p.678),
18.3.7 Stereotype (pp.680–685).

I tre invarianti Stereotype.base_property_* della 2.5.1 non sono dichiarati nel
merged XMI 2.4.1. Le tabelle normative restano 150 operazioni e 433 invarianti.
I controlli del legame runtime hanno identificatori `prose:Stereotype.*`, separati:
un solo oggetto base, upper=1 e lower rappresentato pari a 0 o 1. La 2.4.1 ammette
ruoli base alternativi con i default di molteplicità della vecchia fonte; non si
impone automaticamente lower=0 a tutti i ruoli quando le estensioni sono multiple,
come fa il vincolo aggiunto nella 2.5.1. Questo è il contratto operativo adottato
sulla base del testo/diagrammi della 2.4.1, non un nuovo invariante attribuito all'XMI.

La rimozione di un profilo direttamente applicato è rifiutata finché restano
profili applicati dipendenti, secondo ProfileApplication p.678. Il fallimento
avviene prima di rimuovere applicazioni o tag. La rimozione elimina le istanze del
profilo e conserva gli elementi del metamodel.

Stereotype.associationEndOwnership usa l'altro memberEnd reale: nella 2.4.1 la query
Property.opposite esclude gli estremi posseduti dall'associazione, proprio quelli
richiesti dal predicato. La correzione conserva le differenze della query opposite.

## XMI ed isolamento

Uml241.xmi conserva applicazioni, valori espliciti vuoti/null, enum, riferimenti
condivisi, composizione, istanze separate e isStrict. La Extension UmlLib registra
versione, namespace dei profili e contesto delle istanze. La selezione dei classifier
rispetta il profilo più vicino: due profili annidati con classifier dello stesso nome
e URI distinti non diventano una collisione artificiale.

Un XML indipendente può fornire `profile_bindings={'urn:domain': profile}` e
external_objects/resources espliciti. Binding di altri backend vengono rifiutati.
Import falliti ripristinano anche applicazioni preesistenti su oggetti esterni e
registri dei valori; costruzioni runtime errate sono XmiError in modalità strict,
o dati opachi diagnosticati in modalità permissiva. Profili sconosciuti restano
opachi. Namespace e versioni continuano a essere controllati dal contratto XMI.

Classi, enum, istanze, codec, callback e registri 2.4.1/2.5.1 restano distinti.
`Uml241.profile_values` e `Uml241.profile_filtering` espongono le API isolate.

## Evidenze e limiti

21 scenari indipendenti in tests/test_profiles241.py verificano i contratti,
controesempi, rollback, ereditarietà, cleanup, strict view, import XML indipendenti,
isolamento e round-trip. La suite completa contiene 430 test; registrazione e test
non costituiscono una certificazione UML.

Restano evaluator per tag derivati/default generali, navigazione runtime degli
estremi non navigabili, mapping di metaclassi non UML, completo CMOF/schema/profile
interchange con strumenti vendor e migrazione tra versioni. OCL arbitrario e callback
non sono trasportati/eseguiti dall'XML. Il marker generale UML2.4.1.prose resta per
gli obblighi normativi non ancora decomposti; questo incremento ne copre solo la
parte runtime dei profili descritta sopra.

```console
python -m unittest discover -s tests -p test_profiles241.py -q
python -m scripts.verify_xmi_corpus --complex --semantic-version 2.4.1
```
