# Piano di completamento di UmlLib

Stato di riferimento: versione 0.2.0, 12 ottobre 2026.

## Obiettivo e ambiti

La priorità è una libreria Python affidabile per creare, leggere, modificare,
cancellare e validare modelli del core UML 2.5.1, con semantica implementata in Python.
Il completamento viene dichiarato per ambiti verificabili:

1. Core: sintassi astratta, proprietà, associazioni, operazioni del metamodel e
   validazione dei modelli.
2. Profili: definizione e applicazione degli stereotipi e gestione delle loro proprietà.
3. Scambio dei modelli: importazione/esportazione XMI, compresi i profili.
4. Diagrammi: modello UMLDI e scambio delle informazioni dei diagrammi.

Un editor grafico e un motore di esecuzione generale di attività/state machine
sono progetti ulteriori. La libreria deve preservare e analizzare quei modelli;
eseguire tutte le azioni UML non è un prerequisito della prima milestone del core.
Le dichiarazioni di conformità devono distinguere gli ambiti del capitolo 2 della
specifica, anziché usare una sola etichetta «UML completo».

## Punto di partenza

- 242 metaclassi e 13 enumerazioni, suddivise in 14 package.
- 203 operazioni concrete, 2 dichiarazioni astratte e 73 proprietà derivate registrate.
- 449 invarianti registrati: registrazione non equivale a verifica della semantica.
- 117 test; 18 regole con collegamenti espliciti agli esempi comportamentali.
- Wheel, archivio sorgente, CI su Python 3.10/3.12/3.14 e pubblicazione già funzionanti.
- InformationFlow, decomposizioni e stereotipi hanno ricevuto un primo audit mirato;
  non vanno trattati come aree definitivamente certificate.

## Sequenza di lavoro

| Fase | Priorità | Dipendenze | Risultato verificabile |
| --- | --- | --- | --- |
| 1. Inventario e tracciabilità | P0 | Stato attuale | Matrice completa dei requisiti e delle lacune |
| 2. Contratti e ciclo di vita | P0 | 1 | Runtime coerente anche dopo modifiche e cancellazioni |
| 3. Audit dei package core | P0 | 1, runtime di 2 | Regole e query verificate con esempi indipendenti |
| 4. Profili completi | P1 | 2, package fondazionali di 3 | Applicazioni e valori degli stereotipi gestiti coerentemente |
| 5. Obblighi contestuali | P1 | 3, 4 | Adattatori e mappature con contratti e limiti espliciti |
| 6. XMI | P1 | Runtime stabile, 4; fatti di 5 ove necessari | Scambio dei modelli senza perdita dei dati supportati |
| 7. StandardProfile e UMLDI | P2 | 4, 6 | Copertura degli artefatti standard aggiuntivi |
| 8. Chiusura e stabilizzazione | P0 per il core | Milestone dell'ambito dichiarato | Release stabile con evidenze e limiti controllati |

La fase 8 ha un primo gate al completamento del core, poi gate separati per
profili, XMI e diagrammi. Non richiede di attendere un editor grafico.

## 1. Inventario e tracciabilità

- Estendere il rapporto oltre i 449 invarianti: proprietà strutturali, firme,
  precondizioni, eventuali postcondizioni, derivazioni e requisiti descritti in prosa.
- Collegare i test esistenti alle rispettive definizioni; i 431 invarianti senza
  collegamenti espliciti non sono automaticamente 431 invarianti senza test.
- Distinguere gli stati «da verificare», «verificato nei casi dichiarati»,
  «parziale», «dipendente dal contesto» e «incongruenza della fonte».
- Per ogni voce registrare fonte/XMI ID, implementazione, esempi, limiti e lavoro residuo.
- Rivedere SPECIFICATION_NOTES.md: una correzione personale di un refuso non è
  automaticamente una correzione normativa. Registrare la precedenza delle fonti,
  eventuali errata ufficiali e l'effetto della scelta sulla dichiarazione di conformità.

**Completamento:** tutti i requisiti del core sono censiti; il rapporto rende visibili
le parti parziali e non presenta il numero di funzioni registrate come percentuale
di conformità. I collegamenti ai test risolvono a esempi realmente eseguibili.

## 2. Contratti delle operazioni e ciclo di vita

- Controllare tipo, molteplicità, ordinamento e unicità dei risultati delle operazioni,
  oltre agli argomenti già controllati.
- Verificare precondizioni e dispatch delle ridefinizioni, inclusi i conflitti di nome
  fra proprietà e query nell'ereditarietà multipla.
- Definire una cancellazione logica esplicita, con politica per figli composti,
  riferimenti esterni, associazioni inverse e applicazioni di stereotipi.
- Rendere la cancellazione indipendente dal momento in cui Python libera l'oggetto:
  l'estensione usata da allInstances deve riflettere lo stato logico del modello.
- Verificare subset, ridefinizioni, derivazioni, proprietà in sola lettura,
  reparenting e rollback di mutazioni che coinvolgono più oggetti.
- Precisare gestione dei riferimenti fra sessioni e di metamodel condivisi.
- Rendere le diagnostiche localizzabili: elemento, proprietà/regola, causa e percorso
  del modello, preservando la compatibilità dell'API di validazione esistente.

**Completamento:** scenari di creazione/modifica/cancellazione non lasciano riferimenti
incoerenti; un'operazione con risultato illegale viene segnalata; ogni operazione
fallita lascia il modello nello stato precedente previsto dal contratto.

## 3. Audit della semantica, package per package

Ordine basato sulle dipendenze:

1. CommonStructure e Values.
2. Classification e SimpleClassifiers.
3. Packages e StructuredClassifiers.
4. CommonBehavior e StateMachines.
5. Activities e Actions.
6. Interactions.
7. UseCases, Deployments e InformationFlows.

Per ogni operazione, derivazione e vincolo:

- Confrontare codice, firma, formula e descrizione normativa.
- Preparare modelli con risultati attesi derivati dalla specifica, non dal codice.
- Coprire casi validi, invalidi e limiti pertinenti: null opzionale, collezione vuota,
  infinito, ereditarietà, cicli, riferimenti esterni e combinazioni fra package.
- Usare scenari condivisi solo quando verificano davvero più regole, con tutti i
  collegamenti dichiarati; non creare centinaia di test che ripetono la funzione.
- Correggere l'implementazione e aggiungere una regressione per ogni difetto trovato.
- Verificare l'effetto delle mutazioni su regole e proprietà derivate già controllate.

**Completamento per package:** ogni requisito è revisionato e collegato alle evidenze
pertinenti; ogni limite o incongruenza residua è esplicito. Il gate del core richiede
che non rimangano obblighi applicabili ignorati o considerati validi per default.

## 4. Profili e stereotipi

- Gestire valori delle proprietà degli stereotipi: tipi, default, molteplicità,
  enumerazioni, ereditarietà, ridefinizioni e riferimenti.
- Gestire proprietà composite e loro ciclo di vita durante rimozione dei profili.
- Implementare e verificare isStrict, visibilità e disponibilità delle metaclassi.
- Verificare applicazione di profili annidati/importati, coesistenza di profili e
  proprietà ereditate da stereotipi in altri profili.
- Allineare API runtime e rappresentazione InstanceSpecification/Slot.
- Fornire un contratto per vincoli personalizzati implementati in Python; dichiarare
  il trattamento dei vincoli espressi in altri linguaggi.

**Completamento:** gli esempi di profili supportati attraversano definizione,
applicazione, aggiornamento e rimozione senza perdere dati ordinari del modello;
valori illegali, duplicati e applicazioni richieste mancanti vengono diagnosticati.

## 5. Espressioni e informazioni dipendenti dal contesto

- Definire il contratto degli adattatori per riferimenti, costanza, effetti collaterali,
  tipi di collezione e valori delle espressioni nei linguaggi dichiarati supportati.
- Distinguere fatti analizzati, fatti dichiarati dall'applicazione e fatti mancanti.
- Completare contratti, invalidazione e controllo delle mappature di gate, occorrenze
  e frammenti extra-globali quando gli oggetti vengono modificati o cancellati.
- Definire il trattamento degli estremi esterni dei messaggi lost/found.
- Stabilire quali fatti sono desumibili dal core UML e quali richiedono dati
  aggiuntivi; non promettere di dedurre informazioni assenti dal modello.

**Completamento:** un caso determinabile è verificato; un fatto mancante viene
segnalato come non valutabile. Nessun linguaggio sconosciuto viene eseguito o
considerato valido implicitamente. I casi dipendenti dal contesto hanno esempi sia
con informazione sufficiente sia senza.

## 6. Importazione ed esportazione XMI

- Gestire identità stabili, riferimenti locali/esterni, namespace, enum e valori.
- Importare i modelli in più passaggi e ricostruire proprietà, oppositi e ownership.
- Gestire profili, applicazioni e valori degli stereotipi.
- Preservare o segnalare esplicitamente informazioni aggiuntive non standard;
  scegliere un formato di estensione per le annotazioni runtime necessarie.
- Verificare round trip sull'identità e sul significato dei modelli, non sull'ordine
  dei caratteri XML.
- Verificare gli obblighi di compatibilità delle versioni XMI indicati dalla specifica
  prima di dichiarare conformità allo scambio dei modelli.
- Confrontare fixture indipendenti, incluse esportazioni di altri strumenti quando
  disponibili, documentando le differenze e senza assumere che un altro tool sia infallibile.

**Completamento:** ogni classe concreta e forma di valore supportata compare in una
suite di scambio; i modelli verificati sopravvivono a import/export senza perdere dati
o cambiare il risultato delle validazioni applicabili.

## 7. StandardProfile e UMLDI

- Distribuire e verificare gli stereotipi del StandardProfile mediante il runtime dei profili.
- Aggiungere le classi UMLDI e i relativi riferimenti agli elementi del core.
- Verificare import/export dei diagrammi con forme, collegamenti, etichette e geometria.
- Tenere il modello dei diagrammi separato dal rendering e dall'editor grafico.

**Completamento:** fixture standard di profili e diagrammi sono importabili,
modificabili e riesportabili; gli ambiti supportati sono dichiarati separatamente.

## 8. Gate di release e criterio di fine

Per ciascuna milestone pubblicare codice, regressioni, rapporto aggiornato,
compatibilità/API e note sui cambiamenti. La pipeline esistente deve verificare
generazione riproducibile, test, build e installazione del wheel fuori dal checkout.

La milestone del core è completa quando:

- Tutte le definizioni e tutti i requisiti applicabili sono censiti e revisionati.
- CRUD, associazioni, operazioni, derivazioni e validazione hanno evidenze indipendenti.
- Non rimangono fallimenti noti o implementazioni parziali nascosti nella dichiarazione.
- I requisiti contestuali hanno un contratto utilizzabile e non producono falsi successi.
- Le interpretazioni divergenti della fonte sono risolte oppure delimitano esplicitamente
  l'ambito che si può dichiarare conforme.
- Documentazione e rapporto distinguono il core da scambio, diagrammi ed esecuzione.

I gate successivi aggiungono i requisiti di profili, XMI e UMLDI. La scelta della
licenza di distribuzione rimane una decisione da risolvere per il riuso del progetto;
non è una misura della conformità UML.

## Primo incremento: versione 0.3.0

1. Estendere la matrice e collegare i test esistenti (fase 1).
2. Aggiungere il controllo dei risultati delle operazioni (fase 2).
3. Completare il primo audit di CommonStructure e Values (fase 3).
4. Pubblicare una release con queste evidenze prima di passare ai package dipendenti.

Le stime di durata dei package si ricavano dal primo audit, mantenendo separati
tempo di implementazione, verifica e risoluzione delle incongruenze della fonte.

Il primo incremento aggiunge contratti sui risultati, estende la matrice ai metadati
dell'XMI e collega esempi a tutti i 38 invarianti e alle query/derivazioni dichiarate
in CommonStructure e Values. Sono corretti la sincronizzazione dei subset verso
proprietà ridefinite e il controllo dei valori booleani computabili dei Constraint.
150 test passano; il rapporto distingue verifiche nei casi dichiarati, incongruenze
della fonte, obblighi contestuali e requisiti ancora da revisionare.

Le fasi 1–3 restano aperte: mancano la scomposizione della prosa normativa aggiuntiva,
la revisione degli estremi associativi, il ciclo di vita con cancellazione logica e
gli audit degli altri package. Prossimo incremento: cancellazione logica e relative
associazioni inverse, seguito da Classification e SimpleClassifiers. Le incongruenze
di OpaqueExpression::result e dei flag firstEvent sono delimitate nel rapporto;
non sono considerate risolte per dichiarare piena conformità.

## Secondo incremento: versione 0.4.0

Cancellazione logica implementata con cascade dei figli composti, pulizia dei riferimenti
UML e degli estremi inversi, rimozione dalle estensioni, cleanup degli stereotipi e
invalidazione delle mappature/fatti ufficiali. La sessione trattiene gli elementi vivi
fino alla cancellazione. Politiche restrict/no-cascade e rollback hanno regressioni;
i riferimenti obbligatori rimasti assenti sono segnalati dalla validazione.

Classification e SimpleClassifiers ricevono il primo audit con esempi collegati a
49 invarianti, 41 query, 17 derivazioni e 6 precondizioni. Sono corretti i vincoli
dei parametri template, la sincronizzazione delle associazioni ereditate e il default
UnlimitedNatural. 187 test passano; 244 voci della matrice hanno esempi collegati.

La fase 2 rimane aperta per diagnostiche con percorsi, revisione completa di subset/
ridefinizioni e politica esplicita dei riferimenti tra sessioni oltre al cleanup.
La fase 3 prosegue con Packages e StructuredClassifiers. Restano da scomporre la
prosa normativa e da risolvere/delimitare le incongruenze documentate; l'audit dei
package non equivale a certificazione di ogni proprietà o requisito UML.

## Terzo incremento: versione 0.5.0

Primo audit di Packages e StructuredClassifiers: esempi collegati a tutti i 36
invarianti, 29 query, 20 derivazioni e alla precondizione dichiarata. Sono verificati
import/reexport, profili/estensioni, associazioni e specializzazioni ordinate,
componenti/porte e connettori. I role binding usano ora le associazioni di contesto;
la corrispondenza dei connettori considera i ruoli ereditati del classificatore
che possiede il CollaborationUse. Senza contesto univoco l'obbligo resta unsupported.
206 test passano; 325 voci della matrice hanno esempi collegati.

La matrice delimita le interpretazioni divergenti e marca come parziali l'algoritmo
di PackageMerge, le restrizioni di ProfileApplication.isStrict e l'API completa dei
tagged value/vincoli degli stereotipi. Questi obblighi restano nel lavoro necessario
al completamento; l'audit dei vincoli XMI non li considera automaticamente soddisfatti.
Il prossimo audit nella sequenza della fase 3 è CommonBehavior e StateMachines.

## Quarto incremento: versione 0.6.0

CommonBehavior e StateMachines hanno esempi per 54 invarianti, 35 query, 11 derivazioni
e 8 record di precondizione. La precondizione del finder Behavior è una formula non
booleana nella fonte: è delimitata come incongruenza, non dichiarata risolta.
224 test passano e 433 voci della matrice hanno esempi collegati.

Correzioni: Behavior senza metodo, controlli protocollari nelle regioni annidate,
punti entry/exit posseduti dai composite State, riferimento alla proprietà corretta
nelle ridefinizioni delle regioni e trattamento dei FinalState/null in LCAState.
TimeEvent distingue evidenze numeriche rappresentate da valutazioni/osservazioni
esterne unsupported. Il rapporto rileva gli otto ID duplicati di State/Vertex e conserva
i corpi locali delle operazioni. Le divergenze fonte/prosa sono documentate.

ProtocolConformance resta parziale sul piano della prova comportamentale; esecuzione
generale, clock e scheduler sono fuori dall'audit statico. La fase 3 prosegue con
Activities e Actions, mantenendo aperti gli obblighi già delimitati nei package precedenti.

## Quinto incremento: versione 0.7.0

Activities e Actions hanno esempi collegati a 205 invarianti, 31 dichiarazioni di query
(29 concrete e 2 astratte) e 9 derivazioni. 250 test passano; 678 voci della matrice
hanno esempi espliciti. Sono verificati confini dei nodi strutturati, firme delle
chiamate, link e qualificatori, scope delle variabili, clausole, loop, eccezioni e
percorsi dei flussi attraverso cicli di nodi di controllo.

Correzioni: featuringClassifier scalare nelle StructuralFeatureAction, isolamento
degli archi del produttore ActionInputPin, varianza dell'output delle selezioni,
evidenze numeriche per upperBound/pesi costanti dei flussi. Valori opachi non valutabili
rimangono unsupported; letterali di tipo errato restano invalid, senza falsi successi.

Il rapporto distingue le divergenze fonte/prosa e i requisiti aggiuntivi ancora parziali:
tipi dei token per decisionInput e selezioni/trasformazioni, prova di assenza di effetti
collaterali, esecuzione dei token. L'audit degli invarianti dichiarati non completa
questi obblighi. La fase 3 prosegue con Interactions, poi UseCases, Deployments e
InformationFlows; restano aperti gli obblighi delle altre fasi e dei package precedenti.

## Sesto incremento: versione 0.8.0

Interactions ha esempi collegati a tutti i 49 invarianti dichiarati, 14 query,
una derivazione e tre precondizioni. I casi di PartDecomposition già presenti restano
inclusi. 262 test passano; 742 voci della matrice hanno esempi espliciti.

Correzioni: ordine di visita dei frammenti annidati, risalita del contesto dei guard
dagli InteractionOperand, unicità dei soli gate esterni, risultato nullo di getOperand
e diagnostiche dei limiti numerici opachi. Sono verificati confini e matching dei gate,
firme e wildcard dei messaggi, direzioni dei parametri, lifeline/selector, continuazioni,
esecuzioni, distruzione, cicli di GeneralOrdering e fatti contestuali delle espressioni.

Restano aperti l'ordine parziale completo delle tracce alternative/parallele, la semantica
generale di dati globali/write-once, la collocazione grafica dei guard e le incongruenze
della fonte delimitate nel rapporto. Il controllo XMI delle reply non vincola tutti
i tipi degli argomenti: questa lacuna è esplicita, non dichiarata risolta.
La fase 3 prosegue con UseCases, Deployments e InformationFlows.

## Settimo incremento: versione 0.9.0

UseCases, Deployments e InformationFlows hanno esempi per 18 invarianti, due query
e una derivazione. 273 test passano; 757 voci della matrice hanno esempi espliciti.
Correzioni: tipo dei part di Node e intersezioni dei subject dei UseCase associati.
Sono verificati include con diamanti/cicli, ownership degli extension point, tipi
degli estremi associativi, deployment e manifestazioni, comunicazioni, subset degli
InformationItem e cleanup dei riferimenti e delle mappature dopo cancellazione.

Tutti i 14 package hanno ora un primo audit delle definizioni semantiche dichiarate:
449 invarianti, 205 operazioni (incluse due astratte), 73 derivazioni e 23 precondizioni.
Questo chiude il primo giro di esempi della fase 3, non la piena conformità del core.
Restano requisiti di prosa/struttura da censire, divergenze fonte/prosa da risolvere,
obblighi contestuali e le altre fasi del piano. deployedElement conserva il filtro
Artifact della fonte: l'espansione delle istanze e dei nested artifact resta parziale.

Prossimo lavoro P0: decomporre i requisiti residui di prosa e contratti strutturali,
poi chiudere le lacune statiche del core in ordine verificabile; le fasi di profili
completi, adattatori, scambio XMI e UMLDI rimangono distinte e aperte.

## Ottavo incremento: versione 0.10.0

Censimento operativo delle limitazioni note generato in CONFORMANCE_BACKLOG.md e
conformance-backlog.json: priorità, fonte, prossima azione, porzione già coperta dai
controlli supplementari. Non è ancora il censimento completo della prosa normativa.
CI e release verificano la riproducibilità del censimento e della matrice.

Cinque requisiti statici supplementari sono integrati in validate(): tipi delle
selezioni/trasformazioni, ordine e tipi degli input delle decisioni, valori delle
reply e Component manifestati da deployment configurati di istanze di Artifact.
Il resolver deployed_elements espande le manifestazioni dirette dei classificatori
Artifact delle istanze; la derivazione XMI originale rimane separata e invariata.
280 test passano; 763 record hanno esempi espliciti.

Le evidenze mancanti sui tipi dei token restano unsupported. La purity dei Behavior,
gli Artifact annidati/ereditati, gli slot e le copie runtime non sono provati da questi
controlli. Prossimo P0: audit per famiglie dei contratti strutturali e decomposizione
dei requisiti di prosa residui; le interpretazioni XMI/prosa restano da riconciliare.

## Nono incremento: versione 0.11.0

Audit strutturale delle 950 dichiarazioni: 549 proprietà memorizzate, 73 derivate e
328 estremi associativi. Tutte le 549 dichiarazioni ricevono verifiche di default,
rifiuto dei tipi errati e assegnazione di un valore del tipo dichiarato. Metadati di
tipi, riferimenti subset/redefines e bounds senza riferimenti irrisolti. I casi per
famiglie e i collegamenti puntuali restano distinti da queste verifiche di dichiarazione.
STRUCTURAL_AUDIT.md e structural-audit.json sono rigenerati e verificati dalla CI.

Correzioni: deduplicazione prima dell'upper bound, ordine degli estremi inversi,
semantica di sostituzione delle proprietà ridefinite, alias verso l'estremo più
specifico e protezione delle letture di collezioni di elementi cancellati. Sono
verificati inverse many-to-many, trasferimenti via estremi scalari, rollback di
costruzione/modifica, subset multipli e riferimenti tra sessioni. 291 test passano.

I riferimenti cross-session restano consentiti ma validate segnala cross session
reference: le query allInstances mantengono un'estensione locale. Non è automaticamente
una violazione UML. Restano aperti la prova semantica per ogni estremo associativo,
combinazioni complete di sottotipi/default, sequenze arbitrarie di mutazioni e prosa.
Prossimo lavoro P0: decomporre e chiudere i requisiti normativi residui con evidenze
puntuali, mantenendo distinti contratti dichiarativi, interpretazioni e obblighi esterni.

## Decimo incremento: versione 0.12.0

Valori degli stereotipi tipizzati: ereditarietà/ridefinizioni, default letterali,
molteplicità, readonly, enumerazioni e riferimenti alle metaclassi. ProfileObject
rappresenta istanze dei Class/DataType del profilo, distinte da InstanceSpecification.
Associazioni binarie navigabili, composizione, rollback e cancellazione sono verificati;
un tipo ancora accessibile da un altro profilo applicato conserva le proprie istanze.

isStrict espone viste e creazione controllata, preservando il modello sottostante,
con priorità dei riferimenti, import e conflitti. Vincoli utente tramite callback
Python Boolean esplicite; le API pubbliche impediscono mutazioni durante la valutazione.
313 test passano. Non vengono eseguite stringhe OCL. Restano adattatori per tipi/valori
personalizzati, derivazioni/default non letterali, navigazione runtime non navigabile,
identità dei link ripetuti e interoperabilità CMOF. La fase profili è avanzata ma
non dichiarata esaustiva. Prossimo incremento: contratto di scambio XMI con round-trip
del core e dei valori runtime supportati, mantenendo esplicite le estensioni non gestite.
