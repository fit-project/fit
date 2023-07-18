REPORT_PEC = "Report di verifica della PEC"

TITLE = "FIT"
REPORT = "Report Freezing Internet Tool"
INDEX = "Indice"

DESCRIPTION = "FIT - Freezing Internet Tool è un’applicazione per l'acquisizione forense di contenuti " \
              "come pagine web, e-mail e social media direttamente da internet. <br><br>" \
              "Un browser forense è un software utilizzato per analizzare e recuperare dati da dispositivi elettronici, " \
              "come computer, smartphone o tablet, durante indagini forensi. Questo software consente di accedere a " \
              "informazioni sull'utilizzo del dispositivo, come cronologia delle attività, file e documenti, " \
              "messaggi di testo, immagini e molto altro, in modo da fornire prove che possono essere utilizzate " \
              "in una causa legale."

T1 = "Freezing Internet Tool"
T2 = "Informazioni generali"
CASEINFO = "Informazioni sul caso"
CASEDATA = "Dati sul caso"
TYPED = "Tipo di acquisizione"
DATE = "Data acquisizione"

T3 = "Verifica titolarità dei dati"
T3DESCR = "Nel corso dell'acquisizione, l'utente navigava alcuni siti web. FIT " \
          "procedeva alla verifica di ciascuna connessione mediante routine appositamente implementate. " \
          "In particolare, ai fini di stabilire la titolarità dei domini coinvolti, venivano indicate le " \
          "seguenti informazioni:"

T4 = "Digital Forensics"
T4DESCR = "La digital forensics è l'applicazione scientifica e tecnologica dei principi " \
          "forensi alla raccolta, conservazione, analisi e presentazione dei dati digitali " \
          "in un contesto legale. Questa disciplina è utilizzata per investigare crimini informatici, " \
          "come la frode, il furto di dati o la diffusione di malware, e per recuperare e analizzare informazioni " \
          "da dispositivi elettronici come computer, smartphone e tablet. La digital forensics comprende " \
          "l'utilizzo di strumenti specializzati per analizzare i dati digitali e garantire la validità delle " \
          "prove in un contesto legale. Il lavoro dei professionisti della digital forensics è cruciale per " \
          "aiutare le agenzie investigative e i tribunali a identificare e punire i responsabili di crimini " \
          "informatici e garantire la giustizia."

TITLECC = "La Catena di Custodia"

CCDESCR = "La catena di custodia è un concetto importante in ambito forense che descrive il " \
          "controllo e la documentazione degli spostamenti e delle manipolazioni di una prova "
"durante un'indagine o un processo legale. La catena di custodia garantisce che la prova sia autentica, " \
"non alterata e non contaminata, e che la sua integrità sia mantenuta dal momento della raccolta fino " \
"all'utilizzo in tribunale. Mantenere una catena di custodia affidabile è fondamentale per garantire " \
"che la prova sia valida e adatta a supportare le conclusioni nell'ambito giudiziario."

TITLEH = "Hash"
HDESCR = "L'hash delle prove digitali è un valore univoco che rappresenta i dati " \
         "digitali e che viene utilizzato per verificare l'integrità e l'autenticità " \
         "delle prove. Un hash viene calcolato utilizzando un algoritmo di crittografia a " \
         "sensi unici che trasforma i dati in una stringa di caratteri a lunghezza fissa. Se i dati " \
         "originali vengono modificati, anche l'hash cambia, rendendo facile rilevare eventuali alterazioni. " \
         "In un contesto legale, l'hash delle prove digitali viene spesso utilizzato per verificare che i dati " \
         "originali non siano stati alterati durante il processo di raccolta, conservazione e presentazione delle " \
         "prove. Mantenere un record dell'hash delle prove digitali contribuisce a garantire la loro integrità " \
         "e ad assicurare che siano adatti a supportare le conclusioni in una causa legale."

T5 = "File prodotti dal sistema"
T5DESCR = "Durante l'acquisizione, il sistema ha prodotto una serie di file " \
          "(come screenshot, video dell'intera navigazione, log del traffico di rete, ecc.), identificati " \
          "nella seguente tabella."

NAME = "Nome del file"
DESCR = "Descrizione"
AVID = "Acquisizione video"
HASHD = "File contenente gli hash dei file"
LOGD = "Informazioni generate dai vari componenti del sistema"
PCAPD = "Registrazione del traffico di rete"
ZIPD = "Archivio contenente l'acquisizione"
WHOISD = "File whois"
PNGD = "Screenshot della pagina"
DUMPD = "File di analisi del traffico"
HEADERSD = "Headers della richiesta"
NSLOOKUPD = "Record DNS"
CERD = "Certificato del server"
SSLKEYD = "Chiavi SSL"
TRACEROUTED = "Traceroute dei pacchetti"

T6 = "Hash dei file prodotti dal sistema"
T6DESCR = "Ogni file prodotto dall'infrastruttura viene validato mediante il calcolo degli hash. " \
          "Con questa procedura, ogni singolo file prodotto è immodificabile e può essere fornito " \
          "anche singolarmente mantenendo la validità della Catena di Custodia"

T7 = "File prodotti dall'utente"
T7DESCR = "Tutti i file prodotti dall'utente durante l'acquisizione sono raccolti all'interno " \
          "della cartella compressa avente estensione .zip. Per ognuno di questi file viene riportata " \
          "la dimensione espressa in bytes."
T8 = "Screenshot della pagina"
T8DESCR = "Viene di seguito riportato lo screenshot della pagina navigata durante l'acquisizione."
VERIFI_OK = "La verifica del timestamp del report in formato PDF ha fornito esito positivo. " \
            "Di seguito vengono riportate le informazioni riguardanti l'esito della verifica, il file, " \
            "l'algoritmo di hashing e il servizio di Time Stamp Authority utilizzato per effettuare il controllo."
VERIFI_KO = "La verifica del timestamp del report in formato PDF ha fornito esito negativo. " \
            "Di seguito vengono riportate le informazioni riguardanti l'esito della verifica, il file, " \
            "l'algoritmo di hashing e il servizio di Time Stamp Authority utilizzato per effettuare il controllo."
VERIFICATION = "Verifica del timestamp del report"

CASE = "Cliente / Caso"
LAWYER = "Avvocato"
PROCEEDING = "Tipo di procedimento"
COURT = "Tribunale"
NUMBER = "Numero di procedimento"
ACQUISITION_TYPE = "Tipo di acquisizione"
ACQUISITION_DATE = "Data acquisizione"
NOT_PRODUCED = "File non prodotto"
SIZE = "Dimensione: "
NOTES = "Note"
OPERATOR = "Operatore"