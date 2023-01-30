# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:35:34 2023

@author: https://forum.ubuntu-it.org/viewtopic.php?t=588799 - user: RAI
"""
#! /usr/bin/env python

""" fetch ricevute di consegna

Usage: script.py 'unseen TEXT "Ricevuta di avvenuta consegna"' >> debug.log
"""
import sys, socket, imaplib, email

#
# SET ME PLEASE
# vvvvvvvvvvvvvvvvvvvv
HOST = 'imaps.pec.aruba.it'         # Il server IMAP, p.es. imap.gmail.com
USER = 'USER@pec.it'                # L'indirizzo, p.es. tuoNome@gmail.com
PASS = 'PASSWORD'                   # La password (qui leggibile da tutti !!)
# ^^^^^^^^^^^^^^^^^^^^

#
# default
MAILBOX = 'INBOX'
SSL = True
CONTENT = 'Ricevuta di avvenuta consegna'
VERBOSE = True # True just for DEBUG
#
#


#
# connect host
#
try:
    if SSL:
        imap = imaplib.IMAP4_SSL(HOST)
    else:
        imap = imaplib.IMAP4(HOST)
except socket.error as e:
    print ("socket.error: {}\n".format(e))
    sys.exit(1)

#
# login
#
try:
    result, data = imap.login(USER, PASS)
except imaplib.IMAP4.error as e:
    print ("imaplib.IMAP4.error: {}\n".format(e))
    sys.exit(1)
if result != "OK":
    print ("login fault: {}\n".format(result))
    sys.exit(1)
if VERBOSE:
    print (data)

#
# select mailbox folder
#
result, data = imap.select(MAILBOX)
if VERBOSE:
    nmail = int(data[0])
    s = nmail != 1 and "s" or ""
    print ("You have {} message{} in {}\n".format(nmail, s, MAILBOX))

#
# searching
#
if len(sys.argv) > 1:
    search = " ".join(sys.argv[1:])
else:
    search = "ALL"
search = '('+search+')'
if VERBOSE:
    print ("imap.uid('search', None, {})".format(search))
try:
    result, data = imap.uid('search', None, search)
except imaplib.IMAP4.error as e:
    print (search);
    print (e)
    sys.exit(1)
if result != "OK":
    print ("Search return something wrong. Sorry, exit with error\n")
    sys.exit(1)

#
# fetching
#
list_mail = data[0].split()
if VERBOSE:
    found_mail = len(list_mail)
    s = found_mail != 1 and "s" or ""
    print ( "Your search returned {} message{}".format(found_mail, s) )

read = [] # inizialize the list of mail to mark as `seen'
for uid in list_mail:
    result, data = imap.uid('fetch', uid, '(BODY.PEEK[])')
    if result != "OK":
        continue
    mail = email.message_from_string(data[0][1])
    for part in mail.walk():
        type_ext = part.get_content_type()
        if type_ext == 'text/plain':
            body = part.get_payload(decode=True)
            if CONTENT in body:
                print ( body )
                read.append(uid)

# extra: just in case the xml file turn out to be required as receipt
#        else:
#            filename = part.get_filename()
#            if filename == 'daticert.xml':
#                print (part.get_payload(decode=True))

# End for uid in list_mail

for uid in read: # Only at the end, mark `SEEN' only fetched mails
    imap.uid('STORE', uid, '+FLAGS.SILENT', '(\seen)')

imap.close()
imap.logout()
