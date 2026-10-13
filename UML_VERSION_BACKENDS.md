# Due metamodel indipendenti, un motore condiviso

UmlLib distribuisce due API Python, introdotte nella 0.15.0:

```python
import Uml241 as uml24
import Uml251 as uml25

legacy = uml24.Class(name="Customer")
current = uml25.Class(name="Customer")
assert legacy.semantic_version == "2.4.1"
assert current.semantic_version == "2.5.1"
assert type(legacy) is not type(current)

state = uml24.StateMachine.State(name="Ready")
```

`Uml` e `UML` mantengono il significato 2.5.1. `Uml251` è un alias esplicito delle
stesse classi già pubblicate; non crea una terza identità per il metamodel.
`Uml241` contiene dichiarazioni Python separate per tutte le 242 classi e le 13
enumerazioni. Non è un alias di quelle 2.5.1.

Entrambe le API sono incluse **nello stesso wheel UmlLib**. Non sono ancora due
distribuzioni pip/GitHub separate: separare i nomi delle distribuzioni non aggiunge
isolamento al modello e imporrebbe più pipeline senza vantaggi in questa fase.
Se necessario, il motore comune potrà diventare una dipendenza condivisa dei due
pacchetti di distribuzione. L'API pubblica resta versionata e distinta.

## Isolamento

Le classi 2.4.1 sono generate dal file OMG `UML/20100901/UML.xmi`, elencato come
merged L3 dalla [pagina ufficiale UML 2.4.1](https://www.omg.org/spec/UML/2.4.1).
La provenienza e l'hash della fonte originale sono nel manifest dell'audit.
I namespace XML e le codifiche dei riferimenti sono interpretati dal suo parser
separato. Non vengono trasformate le dichiarazioni in contratti 2.5.1.

Il motore carica gli stessi moduli Python inclusi nel pacchetto sotto un namespace
interno indipendente. Condivide **il codice sorgente**, non le tabelle mutabili:

- Classi, enum, specifiche e mappe di subset/redefinition/associazioni sono separate.
- Transazioni, allInstances, registri dei profili e sessioni sono separati.
- Le tabelle native 2.4.1 contengono soltanto le implementazioni verificate per 2.4.1.
- Riferimenti e literal enum dell'altra versione vengono rifiutati senza modificare
  il valore precedente. Il backend semantico 2.5.1 rifiuta oggetti 2.4.1.

Non si eseguono espressioni OCL lette dal modello. Si caricano soltanto moduli Python
fidati distribuiti dalla libreria, come per una normale importazione del motore.

```python
with uml24.ModelSession() as session24, uml25.ModelSession() as session25:
    a = uml24.Class(name="Old")
    b = uml25.Class(name="New")
    assert session24.elements == {a}
    assert session25.elements == {b}
    # uml24.Property(type=b) solleva TypeError.
```

I gruppi `Uml241.StateMachines`, `Activities`, ecc. sono facade organizzative
coerenti con l'API esistente. Il file normativo merged 2.4.1 è piatto; la collocazione
sorgente resta registrata in ClassSpec.package. Non si attribuisce questa suddivisione
in package al vecchio documento normativo.

## Stato della versione 2.4.1

Sono disponibili costruzione, lettura/scrittura dei valori strutturali, molteplicità,
tipi, subset/redefinition, composizione, inversi memorizzati, ownership, transazioni
e cancellazione secondo le dichiarazioni 2.4.1. La verifica è un primo audit, non
esaustiva per ogni associazione o sequenza di modifiche. I test coprono i casi distintivi:
ereditarietà di Vertex, featuringClassifier, guard obbligatorio, proprietà di State
e loopVariable senza composizione, oltre a isolamento e rollback.

Dalla 0.17.0 tutte le 14 famiglie hanno un primo audit: 150 operazioni, 433 invarianti,
74 derivazioni e 952 record strutturali. 549 setter osservabili sono attraversati
con default, tipi errati e valori del tipo dichiarato. Le traduzioni condivise sono
abilitate esplicitamente dopo il confronto; le differenze mantengono funzioni
separate. Fonte, interpretazioni ed evidenze sono in [UML241_AUDIT.md](UML241_AUDIT.md)
e `uml241-audit.json`. CommonStructure/Values conserva il suo rapporto dettagliato.

Fatti mancanti sulle espressioni o sull'esecuzione compaiono come obbligazioni
unsupported nella validazione. La navigazione strutturale generica
di owner/ownedElement e delle union è condivisa. `validate()` segnala ancora
`('unsupported version contract', 'UML2.4.1.prose')`: la prosa non è ancora auditata.

Dalla 0.18.0 load/dump XMI 2.4.1 usa il backend nativo isolato; API, selezione
automatica, grafi e limiti sono descritti in [XMI241_SUPPORT.md](XMI241_SUPPORT.md).
Le applicazioni runtime di profili restano disabilitate; definizioni strutturali
Profile/Stereotype e ProfileApplication sono scambiabili. I tag applicati sono
diagnosticati e, in modalità permissiva, conservati come XML opaco. Non è ancora
implementata una conversione tra i due metamodel.

## Rigenerazione e lavoro successivo

```console
python generate_uml.py --version all
```

Il generatore predefinito continua a produrre 2.5.1; `--version 2.4.1` genera soltanto
Uml241. Le pipeline rigenerano entrambe le versioni e verificano l'installazione.

Il primo audit delle famiglie e delle dichiarazioni strutturali è concluso nella
0.17.0; non è una certificazione. Restano prosa globale, esecuzione/protocolli,
PackageMerge, profili runtime, ulteriori adattatori XMI e migrazione, seguendo
[UML_VERSION_COMPARISON.md](UML_VERSION_COMPARISON.md). Questi sono contratti distinti
e non vengono abilitati semplicemente cambiando un namespace XML.
