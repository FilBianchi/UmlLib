# Confronto UML 2.4.1 → UML 2.5.1

Il supporto versionato previsto per UmlLib riguarda **2.4.1 e 2.5.1**.
UML 2.5 non è un obiettivo di implementazione. Il runtime attuale resta 2.5.1:
Questo audit descrive il confronto iniziale. Dalla 0.15.0 esiste un metamodel
strutturale indipendente Uml241, descritto in [UML_VERSION_BACKENDS.md](UML_VERSION_BACKENDS.md);
validazione semantica completa ed exporter 2.4.1 restano da implementare.

## Fonti e riproducibilità

Sono confrontati i documenti machine-readable elencati dalle pagine ufficiali
[OMG UML 2.4.1](https://www.omg.org/spec/UML/2.4.1) e
[OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1):

- Metamodel UML completo/merged L3: `20100901/UML.xmi` e `20161101/UML.xmi`.
- PrimitiveTypes delle due versioni.
- StandardProfileL2 + StandardProfileL3 per 2.4.1, StandardProfile per 2.5.1.

La pagina 2.4.1 elenca file machine-readable descritti come **v2.4**. Sono le fonti
pubblicate da OMG per quella release, non file ricostruiti da Eclipse. Per chiudere
la conformità 2.4.1 occorrerà verificare anche Infrastructure/Superstructure PDF e
le loro correzioni: il confronto XMI non sostituisce la revisione della prosa.
Il metamodel 2.5.1 scaricato coincide con quello già vendorizzato in UmlLib dopo
la normalizzazione delle dichiarazioni.

Le sette fonti XML sono fissate per URL, dimensione e SHA-256 in
[scripts/uml-version-sources.json](scripts/uml-version-sources.json). I file originali
restano nella cache ignorata, senza redistribuzione nel pacchetto.

```console
python -m scripts.compare_uml_versions --fetch
```

Senza `--fetch` è richiesta la cache locale. Il comando verifica gli hash e rigenera
[uml-version-comparison.json](uml-version-comparison.json), che contiene tutte le
differenze dichiarative rilevate, incluse le rappresentazioni prima/dopo.
Non usa il parser del runtime 2.5.1 per interpretare il metamodel 2.4.1.

## Inventario verificato

| Dichiarazioni nel metamodel completo | 2.4.1 | 2.5.1 | Differenze |
| --- | ---: | ---: | --- |
| Classi | 242 | 242 | Stessi nomi e flag; cambia l'ereditarietà di State e Vertex |
| Enumerazioni | 13 | 13 | Stessi nomi e literal, nello stesso ordine |
| Proprietà, inclusi estremi posseduti dalle associazioni | 952 | 950 | 10 nuove, 12 rimosse, 53 dichiarazioni comuni modificate |
| Associazioni | 418 | 418 | 8 nomi sostituiti; le 410 comuni hanno estremi e flag invariati |
| Operazioni | 150 | 205 | 66 nuove, 11 rimosse, 20 dichiarazioni comuni modificate |
| Regole XMI complessive | 597 | 674 | 159 nuove, 82 rimosse, 482 comuni con testo/riferimenti diversi |
| Regole possedute direttamente dalle classi | 433 | 449 | Conteggio separato da body condition e pre/postcondizioni |
| PrimitiveTypes | 5 | 5 | Boolean, Integer, Real, String, UnlimitedNatural invariati nelle dichiarazioni confrontate |

La collocazione delle classi cambia: il file 2.4.1 è un merged model piatto;
quello 2.5.1 le distribuisce nei package. Tutte le 242 collocazioni cambiano,
ma **240 classi conservano la stessa ereditarietà diretta**. Questo cambio di
organizzazione del documento non deve generare 242 incompatibilità nel modello utente.

Le differenze sono confrontate per nomi dichiarativi, normalizzando ID, riferimenti
in attributi/elementi, namespace XML e default MOF delle caratteristiche confrontate.
Le operazioni includono firma, parametri e riferimenti alle condizioni; i testi
delle condizioni sono inventariati separatamente. Gli stub di riferimento non sono
contati come nuove classi. I nomi dei parametri e delle regole fanno parte del
confronto: una rinomina può comparire come rimozione/aggiunta o firma modificata.
I conteggi non indicano altrettante incompatibilità semantiche indipendenti.

## Differenze che incidono sui modelli

| Area | Dichiarazioni verificate | Conseguenza per UmlLib |
| --- | --- | --- |
| StateMachines | Vertex acquisisce RedefinableElement; State lo eredita tramite Vertex | La validazione dei vertici e delle ridefinizioni deve dipendere dalla versione |
| StateMachines | State.redefinedState/redefinitionContext sono sostituite da Vertex.redefinedVertex/redefinitionContext | Occorre una mappa esplicita dei nomi e delle restrizioni; il downgrade di vertici non-State richiede diagnosi |
| Classification | Feature.featuringClassifier passa da 0..* a 0..1 | Una feature 2.4.1 condivisa da più classifier non si converte automaticamente senza perdita |
| Activities | ActivityEdge.guard/weight, JoinNode.joinSpec e ObjectNode.upperBound passano da 1 a 0..1 | Cambiano i requisiti di presenza; il downgrade deve applicare solo default semanticamente giustificati |
| Actions | LoopNode.loopVariable diventa composito e subset di Element.ownedElement | Cambiano owner, cancellazione e serializzazione; riferimenti condivisi richiedono una decisione esplicita |
| Multiplicities | MultiplicityElement.lower/upper passano da 0..1 con default dichiarato a 1..1 senza quel default dichiarato | Vanno confrontate le derivazioni, senza confondere default di serializzazione e significato UML |
| Ordered features | Cambiano isOrdered di AcceptEventAction.result, Association.endType, Classifier.attribute, ConnectableElement.end, DurationObservation.event, ReplyAction.replyValue, StringExpression.subExpression e UnmarshallAction.result | L'import/export deve conservare l'ordine dove richiesto dalla versione |
| Proprietà | Property.default scompare; scompare la dichiarazione locale Property.isReadOnly | Property.default necessita di una policy; isReadOnly resta disponibile per ereditarietà e non va rifiutata solo perché manca la ridefinizione locale |
| Association-owned ends | Sei associazioni rinominano l'estremo inverso; altre due seguono State → Vertex | Gli alias devono essere specifici della versione e distinti da un cambio semantico |

Ulteriori cambiamenti di upper bound, subset/redefinition, default e flag degli
estremi inversi sono elencati integralmente nel JSON. La tabella evidenzia i rischi
che impediscono di dichiarare una conversione generale senza perdita.

## Operazioni, OCL e prosa

Tra le nuove operazioni figurano query di Actions/Activities, parametri di Behavior
e CallAction, interfacce di Classifier, Gate e MessageEnd e query di Vertex.
Tra le rimozioni figurano query locali di Component, Property.default e
MultiplicityElement.includesCardinality. Alcune responsabilità sono trasferite a
query generali: non sono 11 funzionalità necessariamente eliminate.

Delle 597 regole del vecchio file, 515 hanno la stessa chiave nel nuovo; 33 di queste
conservano espressioni e riferimenti normalizzati, 482 differiscono. Il confronto
preserva gli spazi dentro i literal OCL e normalizza gli spazi esterni.
Questo è **un inventario dei candidati alla revisione**, non una prova di equivalenza
o divergenza OCL. Una riscrittura equivalente non richiede una seconda implementazione;
una modifica della prosa può invece richiederla anche se l'espressione è invariata.

La revisione semantica dovrà coprire anche i requisiti solo testuali, derivazioni,
regole ereditate e assunzioni degli algoritmi Python. Il report non è una
certificazione di conformità né un confronto completo frase per frase dei PDF.

## StandardProfile e formati XMI

Le due fonti L2/L3 contengono in totale gli stessi **33 nomi di stereotipi** del
nuovo StandardProfile e le stesse 34 estensioni dichiarate. Cambiano:

- URI/package del profilo: L2/L3 vengono unificati in StandardProfile.
- File passa da stereotipo astratto a concreto.
- Derive.computation non compare più: 69 dichiarazioni di proprietà diventano 68.
- Le dieci regole presenti nelle fonti L2 non compaiono nel nuovo XMI del profilo.
  Questo dato non basta a concludere che siano abolite tutte le prescrizioni della prosa.

Il metamodel 2.4.1 usa namespace UML/XMI `20100901`, attualmente non riconosciuti dal
reader UmlLib; il riconoscimento di `20110701` non equivale al supporto di quella
fonte. Il metamodel 2.5.1 dichiara namespace `20131001` pur essendo pubblicato sotto
`20161101`. Il namespace da solo non identifica sempre la versione semantica.
Non viene introdotto un alias 20100901 che importerebbe silenziosamente con regole 2.5.1.

## Piano operativo per le due versioni

1. **Inventario completato:** dichiarazioni del merged metamodel, primitivi e profilo
   standard, fonti con checksum, differenze riproducibili e casi di incompatibilità.
2. **Contratto di versione:** versione semantica esplicita del modello e del validatore;
   registro delle proprietà/regole 2.4.1 separato dal 2.5.1, con implementazioni comuni
   dove l'equivalenza è verificata. Un modello 2.4.1 deve poter rappresentare anche
   cardinalità/ownership che il runtime 2.5.1 restringe.
3. **Migrazione strutturale:** mappare State/Vertex e gli estremi rinominati; distinguere
   proprietà ereditate da proprietà eliminate; produrre un rapporto per ogni conversione
   con modifiche, perdite potenziali e incompatibilità. Nessuno scarto silenzioso.
4. **Regole versionate:** revisionare le 482 regole comuni modificate, quelle aggiunte/
   rimosse e la prosa; aggiungere fixture nelle quali la stessa configurazione ha esito
   diverso nelle due versioni, partendo da StateMachines, Classification e Activities.
5. **XMI bidirezionale:** reader/writer 2.4.1, URI e StandardProfile specifici; fixture
   indipendenti nelle due versioni e round-trip. Il downgrade deve rifiutare casi non
   rappresentabili salvo una policy di conversione esplicitamente scelta.

La raccomandazione è condividere il codice Python verificato, mantenendo contratti
e validazione per versione. Una sola etichetta target_version sul runtime attuale
non sarebbe sufficiente a soddisfare il supporto richiesto.
