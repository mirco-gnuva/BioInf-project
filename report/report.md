## INTRODUZIONE
### Dati multi-omici
L'avvento dei dati multi omici, ha permesso di analizzare e studiare i pazienti oncologici non solo dal punto di vista clinico, ma anche molecolare.
L'elevata dimensionalità dei dati, permette così di comprendere a fondo le dinamiche che contraddisitnguono le diverse tipologie di tumori, e di individuare nuovi marcatori molecolari che possano essere utilizzati per la diagnosi e la terapia; lo sfruttamento dei dati multi-omici si rivela quindi abilitante per la medicina di precisione. 
L'eterogeneità dei dati oggi a disposizione, rende però necessario lo studio di specifiche tecniche di integrazione che permettano di sfruttare le informazioni infra e inter-omiche.

### Medicina di precisione
La medicina di precisione è una nuova metodologia di trattamento del paziente che si basa sulla personalizzazione della terapia in base alle caratteristiche peculiari del paziente. Questo approccio è particolarmente efficace in oncologia, dove la variabilità dei tumori e delle risposte alle terapie è molto elevata. L'obiettivo è quello di identificare i sottotipi di tumore e di individuare le terapie più efficaci per ciascun paziente. L'analisi dei dati multi-omici è fondamentale per raggiungere questo obiettivo, in quanto permette di ottenere una visione più completa e dettagliata del paziente e del suo tumore.

#### Identificazione sottotipi di tumore
Vista la notevole eterogeneità dei tumori, è necessario identificarne i sottotipi, in modo da poter creare terapie mirate. Sottotipi di uno stesso tumore possono implicare differenti prognosi e risposte alle terapie. Anche in questo caso, trovare il metodo più efficace per integrare le diverse tipologie dei dati gioca un ruolo fondamentale nel raggiungimento di risultati significativi. Ottenere una rappresentazione unificata dei vari aspetti, preservando le informazioni sia speicifiche di ogni 'vista' che quelle che emergono dal confronto con le altre è una sfida aperta e oggetto di numerosi studi.

Oltre alla problematica dell'integrazione dei dati, è anche necessario inidividuare la tecnica migliore di clustering dei pazienti per massimizzare l'identificazione dei sottotipi di tumore. Un aspetto da non sottovalutare nel clustering è la forte dipendenza dei risultati dagli iperparametri scelti. La scelta di questi ultimi è spesso basata su criteri empirici e non sempre supportata da evidenze scientifiche ciò intacca la riproducibilità dei risultati.


### Progetto TCGA
Il progetto TCGA (The Cancer Genome Atlas) è un progetto di ricerca che ha lo scopo di raccogliere dati multi-omici riguardanti 33 tipologie di tumore su più di 85000 pazienti.
L'accesso libero a tale quantità di dati, permette di ideare e confrontare diverse tecniche di analisi accelerando così la ricerca in campo oncologico.


## METODI
### Dati
I dataset utilizzati riguardano il tumore alla prostata e sono stati scaricati dal progetto TCGA. Si suddividono in:
- Proteomici (Espressione proteica)
- Trascrittomici (mRNA)
- Epigenomici (miRNA)
- Riguardo il fenotipo
- Sottotipi di tumore individuati tramite framework iCluster


#### Confronto sorgenti
Come è possibile notare dalla tabella sottostante, il dataset riguardo i dati trascrittomici presenta molte più feature rispetto alle altre due sorgenti; questo elemento potrebbe influenzare i risultati dell'integrazione. Se da un lato, la numerosità delle feature rende necessario mettere in atto strategie di riduzione della dimensionalità, dall'altro, è più probabile perdere informazioni rilevanti se il numero finale di feature è molto basso.

|          | Pazienti | Features |
|----------|----------|----------|
| Proteine | 352      | 195      |
| miRNA    | 547      | 1046     |
| mRNA     | 550      | 20501    |


#### Sottotipi di tumore
La distribuzione dei sottotipi [PLOT] presenta uno sbilanciamente percentuale rilevante tra i sottotipi 3 e 1 il che rende consigliabile valutare l'oversampling della classe minoritara e/o l'undersampling del sottotipo 3.  



#### iCluster
iCluster è un framework che permette di dentificare sottotipi da tumore integrando dati multi-omici. L'obiettivo è quello di considerare contemporaneamente:
- Varianza delle singole feature
- Covarianza intra-omica
- Covarianza inter-omica

In questo modo, l'idea è quella di sfruttare l'informazione data dalle singole fonti, senza ignorare le interazioni tra di esse.
Vista la necessità di gestire una mole di dati attualmente proibitiva, viene applicata la tecnica PCA in modo da ridurre la dimensionalità dei dati, senza perdere informazioni significative. Visto l'utilizzo di una tecnica di feature-extraction, le dimensioni post applicazione non sono quelle originali ma proiettano il dato in uno spazio latente.



### Preprocessing
Ogni sorgente di dati, viene processata attraverso una specifica pipeline. Lo scopo delle pipeline è quello di uniformare i dati eliminando i risultati relativia a campioni non utili ai fini della sperimentazione.

#### Pipeline miRNA, mRNA, dati proteomici
##### Selezione tumore principale
Vengono eliminati tutti i risultati campioni che non siano relativi al tumore principale.
[PERCHÈ?]

##### Gestione valori mancanti
L'unica sorgente che presenta dati mancanti è quella relativa all'espressione proteica (4.5%)[PLOT]. 
Ognuna di tali feature, presenta almeno il 40% di valori mancanti [PLOT]; perciò assumendo che la loro rimozione non comporti una perdita significativa di informazione, vengono eliminate dal dataset. Questa è un'assunzione molto forte che andrebbe analizzata a fondo considerando indici di correlazione come il coefficiente di Pearson.


##### Riduzione di dimensionalità
Come accade in iCluster, per facilitare la gestione di dati ad alta dimensionalità come quelli scelti; si è reso necessario limitare il numero di feature.
Per garantire una maggiore interpretabilità dei risultati da parte di persone esperte del dominio, si è preferito non proiettare i campioni in uno spazio latente, ma attuare una selezione delle feature più significative.
Come nello step precedente, si è fatta un'assunzione altrettanto forte: Le feature con una maggiore variabilità dei valori sono quelle più significative.
Questa scelta viene supportata a livello intuitivo dal fatto che se, al variare del sottotipo, i valori in una certa dimensione rimangono costanti, allora essi non sono rilevanti.
Per ogni feature di ogni sorgente viene quindi calcolata la varianza e vengono selezionate solo le prime 100 feature con la maggiore varianza.


##### Troncamento barcode
I barcode della piattaforma TCGA, costituiti da 24 caratteri, contengono informazioni non necessarie per l'integrazione dei dati. Vengono quindi troncati a 12 caratteri, il che permette comunque di identificare univocamente i campioni.


#### Pipeline dati fenotipo
In questo caso, dato che i dati relativi al fenotipo dei pazienti non sono oggetto di integrazione, la pipeline [PLOT] risulta molto più semplice.
I campioni presenti nei dataset analizzati sono stati conservati tramite due metodologie diverse: FFPE e confelamento. 
Dato che i campioni congelati si conservano meglio, si è scelto di eliminare i campioni FFPE. Questo permette in un secondo momento, di eliminare tali campioni anche dagli altri dataset semplicemente intersecando i barcode.


#### Pipeline comune
Ogni sorgente, compresa quella dei sottotipi, condividono una pipeline di preparazione all'integrazione. Tale pipeline modifica la struttura dei dataset come segne:
1. Interseca i barcode dei campioni in modo tale che le sogenti condividano gli stessi campioni
2. Ordina i campioni in base al barcode in modo tale che l'integrazione si possa basare sulla posizione, semplificando la pipeline d'integrazione


### Matrici di similarità 
Siccome ogni strategia di integrazione messa in atto nello step successivo richiede il calcolo di una matrice di similarità per ogni sorgente, si è scelto di rendere indipendente tale passaggio.
Il calcolo della similarità avviene tramite la scaled exponential euclidean distance, che permette di calcolare la similarità tra due campioni in base alla distanza euclidea tra di essi. [PERCHÈ?]


### Integrazione
Si è deciso di confrontare le seguenti strategie di integrazione:
- Non integrazione
- Media delle matrici si similarità
- SNF (Similarity Network Fusion)


#### Non integrazione
L'idea alla base della non integrazione è quella di analizzare come ogni sorgente permetta di identificare i sottotipi di tumore rispetto ai risultati ottenuti integrando i dati in modi diversi. Dati i successi nel campo della classificazione dei tipi e sottotipi dei sistemi multi-omici, è lecito considerare le performance delle singole sorgenti come lower bound per le analisi. 

#### Media matrici
Uno dei metodi più semplici per integrare matrici diverse è quello di farne semplicemente la media. Fare la media elemento per elemento comporta diverse problematiche, tra cui il fatto che non vengono tenute in considerazione le relazioni tra le sorgenti e che potrebbe emergere patten dipendenti unicamente dal posizionamento delle feature nei dataset.
Questa strategia di integrazione è quindi utile come baseline per confrontare le performance di metodi più complessi e sofisticati.

#### Similarity Network Fusion
SNF si propone come strategia di integrazione in grado di risolvere tre problemi principali:
- Rapporto segnale/rumore basso
- Dati su scale diverse e bias durante il collezionamento
- Interdipendenza tra le sorgenti

L'algritmo si compone di due step principali:
1. Calcolo della matrice di similarità per ogni sorgente
2. Fusione delle matrici di similarità

In particolare, le matrici di similarità calcolate per ogni sorgente, vengono usate come base per la costruzione di grafi pesati dove i nodi sono i campioni (nella presente sperimentazione, i pazienti) e gli archi rappresentano la similarità tra di essi. Ogni grafo viene poi *fuso* iterativamente. Ad ogni iterazione il grafo risultante viene reso il più simile possibile a tutti gli altri. Il processo continua fino a convergenza.
SNF si dimostra efficace nell'elminare rumori specifici delle sorgenti (ovvero archi con pesi bassi), mantenimento delle relazioni più forti ed esaltazione di connessioni deboli ma presenti in più sorgenti.


### Clustering
Per effettuare il clustering dei pazienti, si è scelto di utilizzare l'algorimto K-medoids.
Il funzionamento di tale algoritmo è molto simile a quello di k-means, con la differenza che i cluster vengono formati partendo dai *medoidi*.
Un medoide, è un punto del dataset che minimizza la somma delle distanze tra di esso e tutti gli altri punti del cluster.
Risulta naturale associare K-means e quindi i centroidi con il concetto di media, mentre i medoidi con la mediana.
Così come la media dipende dalla distribuzione dei dati e quindi è sensibile agli outliers, anche i cluster identificati da K-means lo saranno.
I medoid in vece, come la mediana, rappresentano i valori centrali nell'ordinamento degli elementi del cluster.

K-medoids tuttavia condivide con K-means la necessità di specificare il numero di cluster da identificare. Questo è un problema aperto e non esiste una soluzione univoca. Inoltre, la scelta del numero di cluster è molto importante e può influenzare fortemente i risultati del clustering. Nel caso specifico della presente sperimentazine la scelta è stata guidata dal numero di sottotipi precedentemente identificati tramite iCluster.

## RISULTATI
### Metriche di valutazione
Per valutare la qualità dei clustering ottenuti, si è scelto di utilizzare le seguenti metriche:
- Rand Index
- Adjusted Rand Index
- Normalized Mutual Information 
- Silhouette Score

#### Rand Index
Il Rand Index è una metrica che misura la similarità tra due clustering. Il valore ottenuto può variare tra 0 e 1, dove 0 indica che i due clustering non sono simili, mentre 1 indica che i due clustering sono identici.
Viene definito come:
$ RI = \frac{\alpha + \beta}{N}$

Dove:
- $\alpha$ è il numero di coppie di elementi che sono nello stesso cluster in entrambi i clustering
- $\beta$ è il numero di coppie di elementi che sono in cluster diversi in entrambi i clustering
- $N$ è il numero totale di coppie di elementi

Essendo una metrica dalla definizione intuitiva, è stata scelta per aumentare l'interpretabilità dei risultati.


#### Adjusted Rand Index
L'Adjusted Rand Index è una versione corretta del Rand Index che tiene conto del fatto che il Rand Index tende ad essere alto anche per clustering casuali. Più nello specifico, viene calcolato il RI, che viene poi *corretto* con il suo valore attesto. In questo modo viene considerata l'eventualità che il clustering sia frutto del caso.
La sua definizione è:
$ ARI = \frac{RI - E[RI]}{max(RI) - E[RI]}$


#### Normalized Mutual Information
La Normalized Mutual Information è una metrica che misura la similarità tra due clustering. Il valore ottenuto può variare tra 0 e 1, dove 0 indica che i due clustering non sono simili, mentre 1 indica che i due clustering sono identici. Esprime quanto le informazioni di un clustering siano utili per prevedere l'altro. Quindi se l' NMI è 1, esiste una relazione perfetta tra i due clustering.
Viene definita come:
$ NMI = \frac{I(X;Y)}{\sqrt{H(X)H(Y)}}$


#### Silhouette Score
Differentemente dalle precedenti metriche, il Silhoutte Score non dipende da un clustering di riferimento. Misura la qualità del clustering in base alla distanza media tra i campioni di uno stesso cluster e la distanza media tra i campioni di cluster diversi. Il valore ottenuto può variare tra -1 e 1.
Un valore alto significa che, mediamente, i punti sono più vicini al proprio cluster rispetto a quelli circostanti, un valore basso indica che i punti sono più vicini a cluster diversi rispetto a quello di appartenenza mentre 0 indica che i punti sono equidistanti dai cluster vicini e quindi è probabile che due o più cluster siano sovrapposti.

Lo score per ogni punto viene calcolato come:
$ S = \frac{b - a}{max(a, b)}$

Dove:
- $a$ è la distanza media tra un campione e tutti gli altri campioni nello stesso cluster
- $b$ è la distanza media tra un campione e tutti i campioni di un cluster diverso da quello di appartenenza
- $max(a, b)$ è il massimo tra le due distanze

Il Silhouette Score è la media dei valori ottenuti per ogni campione.


### R