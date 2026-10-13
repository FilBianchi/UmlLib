# Audit UML 2.4.1 — 0.17.0

Completato il primo audit di tutte le 14 famiglie dell'API: CommonStructure,
Values, Classification, SimpleClassifiers, Packages, StructuredClassifiers,
CommonBehavior, StateMachines, Activities, Actions, Interactions, UseCases,
Deployments e InformationFlows. La fonte resta il merged XMI OMG 2.4.1 vendorizzato;
le famiglie sono facade organizzative, non package inventati nella fonte piatta.

Il report riproducibile `uml241-audit.json` inventaria 150 dichiarazioni di operazioni,
433 invarianti e 74 proprietà derivate, senza registrazioni mancanti o aggiunte alle
tabelle normative. Ogni record rimanda alla fonte, alla descrizione/formula e al
meccanismo Python. Le traduzioni comuni sono abilitate esplicitamente nel backend
isolato 2.4.1; quelle differenti sono separate nei moduli `semantics241_*`.
I 56 helper di dipendenza sono elencati separatamente e non contano come operazioni
normative aggiuntive. Non è un interprete OCL né una certificazione di conformità.

## Decisioni rispetto alla fonte

CommonStructure/Values e import sono descritti in
[UML241_COMMON_VALUES_AUDIT.md](UML241_COMMON_VALUES_AUDIT.md). Per le altre famiglie:

| Ambito | Implementazione e interpretazione |
| --- | --- |
| Classifier/Class/DataType | `Classifier.inherit` restituisce gli elementi ricevuti; Class e DataType filtrano quelli ridefiniti. featuringClassifier è una collezione derivata dai feature diretti, come dichiara la 2.4.1. |
| Property/Parameter | default testuali dei literal, `isAttribute(p)` con argomento esplicito, opposite solo tra estremi posseduti da classifier. Default opachi richiedono un adapter; nessuna esecuzione implicita. |
| Ridefinizioni | Operation confronta la covarianza dei tipi dei parametri corrispondenti, correggendo l'indice costante della formula. BehavioralFeature distingue le sequenze di tipi, senza introdurre i campi aggiuntivi della 2.5.1. Property usa upperBound nella clausola che ripete erroneamente lowerBound. |
| Component/Port/Connector | Interfacce realizzate/usate, realizer e coniugazione seguono i link del modello. La compatibilità delle feature è interpretata con identità o nome/metaclasse e firma nominale; non prova equivalenza delle tracce dei protocolli. |
| Port distrutta | `delete()` elimina atomicamente anche i connector che la usano. Il modo restrict resta atomico. La regola temporale `port_destroyed` non viene spacciata per predicato statico: senza storia, `check` segnala unsupported. |
| Behavior/FunctionBehavior | Al massimo un comportamento per proprietario/specification; PrimitiveType è un DataType valido nei parametri di FunctionBehavior. Le feature obsolete non realizzano la specification corrente. |
| StateMachines | ancestor(s1,s2) indica s1 antenato di s2. redefinitionContext segue la vecchia formula. LCA restituisce il Namespace dichiarato (State o StateMachine); il testo menziona anche Region, che non è Namespace: questa ambiguità è risolta a favore del tipo della firma. |
| Estensioni di stati/regioni | I segnaposto `true` vengono sostituiti da controlli sui tipi e sulla struttura conservata/ridefinita. extendedRegion/extendedStateMachine conservano per riferimento la struttura ereditata, senza trasferirne la proprietà composita. Una regione non collegata non può perdere i vertici/transizioni originali. |
| Activities/Actions | Uguaglianza di tipo, ordine e molteplicità dei pin secondo le vecchie clausole; nodi parametro in numero massimo, non esatto. Un insertAt è richiesto sui valori ordinati anche quando isReplaceAll è true. Le query dei limiti non sono confuse con la proprietà omonima di ObjectNode. |
| Activity.structuredNode | Nella 2.4.1 è una collezione derivata da node. La relazione activity trasferisce node/group insieme, rispettando il testimone composito derivato; non si rende scrivibile la proprietà readonly. |
| Unmarshall | Output in ordine con le proprietà, tipi nominali identici e molteplicità compatibili. L'ordine delle proprietà è ricavato dalla dichiarazione ordered di ownedAttribute, non da un metodo inesistente sulla collezione attribute. |
| Interactions | Lifeline ammette classifier antenati del context; un selector presente richiede molteplicità multipla. ConsiderIgnoreFragment ammette anche Reception. Gate impliciti usano le convenzioni in_/out_ della descrizione normativa 2.4.1 (Superstructure, p. 494). I vincoli min/max si applicano ai loop. |
| UseCases/Deployments/InformationFlows | Inclusione transitiva con cicli, associazioni degli Actor, link dei canali e conformance nominale. deployedElement risolve anche InstanceSpecification con classifier Artifact secondo la prosa, oltre alle manifestation dirette degli Artifact. Copie/runtime di deployment e manifestazioni annidate restano fuori dal controllo. |

Le descrizioni testuali delle dichiarazioni sono usate per correggere refusi e corpi
segnaposto. Le decisioni delle traduzioni condivise conservano anche i limiti del
precedente audit 2.5.1, indicati come riferimento separato nel JSON. Non è stata
trasformata in predicati ogni frase dei PDF UML.

## Contratti strutturali ed evidenze

Tutti i 952 record di proprietà/estremi ricevono controlli di metadati: 550 proprietà
memorizzate, 74 derivate e 328 estremi posseduti dalle associazioni. Tipi, bounds e
riferimenti subset/redefinition non hanno diagnostiche irrisolte.

I test attraversano default, rifiuto atomico di tipi errati e un valore del tipo
dichiarato per tutti i 549 setter effettivamente osservabili. L'unica dichiarazione
esclusa dall'esecuzione è StructuralFeature.isReadOnly: è nascosta dalla ridefinizione
Property.isReadOnly su ogni sottotipo concreto; i suoi metadati sono comunque censiti.
Gli estremi association-owned non sono conteggiati come setter generati.

Gli scenari indipendenti coprono le differenze di versione, grafi ereditati, nomi,
molteplicità, proprietà/inversi, rollback, cicli, cancellazione, protocolli, pin,
ordinamento delle interazioni, deployment e information flow. Sono evidenze per
famiglia, non una dimostrazione individuale di tutti i 433 invarianti o di ogni
sequenza possibile di mutazioni. La suite completa ha 392 test.

## Informazioni esterne e limiti

```python
from Uml241.semantic_facts import register_semantic_facts
register_semantic_facts(transformation_behavior, pure=True)
register_semantic_facts(transition, trigger_parameters_assigned=False)
```

Sono fatti Boolean forniti da codice fidato, isolati nel backend 2.4.1, non inferiti
dal testo. Sono supportati anche autonomous e starting_time_available. In assenza
del fatto necessario il controllo resta unsupported. Per ValueSpecification,
si usano i fatti separati di `Uml241.expression_semantics`; valutazione numerica,
tipi di collezione di dominio e rappresentazioni lessicali esterne richiedono adapter.

Restano obbligazioni distinte: prosa supplementare generale (`UML2.4.1.prose`),
esecuzione dei token/tracce, algoritmo PackageMerge e prova comportamentale di
ProtocolConformance, applicazioni runtime di profili, import/export XMI 2.4.1 e
migrazione tra versioni. La registrazione di tutti i predicati dichiarati non chiude
questi contratti. Le API esistenti 2.5.1 restano isolate e verificate dalla stessa suite.

```console
python -m scripts.report_uml241_complete_audit
python -m unittest discover -s tests -q
```

CI e pubblicazione della release rigenerano il report e verificano che non cambi.
