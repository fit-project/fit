import pecs

# Configurazione dell'account PEC
username = 'tuoindirizzo@emailpec.it'
password = 'tuapassword'

# Informazioni sul messaggio
subject = 'Oggetto della email'
message = 'Testo del messaggio'

# Informazioni sul destinatario
to_address = 'destinatario@email.it'

# Creazione del messaggio PEC
pec_message = pecs.new_message(to_address, subject, message, username, password)

# Aggiunta dei file allegati
with open('file_allegato_1.pdf', 'rb') as f1, open('file_allegato_2.tsr', 'rb') as f2:
    pec_message.add_attachment(f1.read(), 'application/pdf', 'file_allegato_1.pdf')
    pec_message.add_attachment(f2.read(), 'application/octet-stream', 'file_allegato_2.tsr')

# Invio del messaggio PEC
pec_client = pecs.new_client()
pec_client.send_message(pec_message)

print('PEC inviata con successo')