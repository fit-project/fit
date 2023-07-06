#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import imaplib
import email
import io
import os
import email.message
import re
import sys

import pyzmail

class Mail():
    def __init__(self):
        self.email_address = None
        self.password = None
        self.mailbox = None
        self.is_logged_in = False
        self.logs=''

    def check_server(self, server, port):
        # Connect and log to the mailbox using IMAP server
        try:
            self.mailbox = imaplib.IMAP4_SSL(server, int(port))  # imap ssl port
        except Exception as e:
            raise Exception(e)
        self.__save_logs()

    def check_login(self, email_address, password):
        self.email_address = email_address
        self.password = password
        try:
            self.mailbox.login(self.email_address, self.password)
            self.mailbox.select()
            self.is_logged_in = True
        except Exception as e:
            raise Exception(e)
        
        # Clear password after usage
        self.password = ''
        self.__save_logs()


    def get_mails_from_every_folder(self, params):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in self.mailbox.list()[1]:
            name = folder.decode()
            if ' "/" ' in name: #tested by zitelog on imapmail.libero.it
                name = folder.decode().split(' "/" ')[1]
            elif ' "." ' in name: #tested by zitelog on imaps.pec.aruba.it
                name = folder.decode().split(' "." ')[1]
            else:
                name = None
          
            if name is not None:
                folders.append(name)

        # Scrape every message from the folders
        scraped_emails = self.fetch_messages(folders, params)
        self.__save_logs()
        return scraped_emails

    def fetch_messages(self, folders, params=None):
        scraped_emails = {}
        for folder in folders:
            try:
                self.mailbox.select(folder,readonly=True)
                type, data = self.mailbox.search(None, params)

                # Fetch every message in specified folder
                messages = data[0].split()
                for email_id in messages:
                    status, email_data = self.mailbox.fetch(email_id, "BODY.PEEK[HEADER]") #fetch just the header to speed up the process
                    email_part = email.message_from_bytes(email_data[0][1])

                    # prepare data for the dict
                    uid = str(email_id.decode("utf-8"))
                    subject = email_part['subject']
                    date_str = str(email_part['date'])
                    sender = email_part['from']
                    recipient = email_part['to']
                    dict_value = 'Mittente: ' + sender + '\nDestinatario: ' + recipient + '\nData: ' \
                                 + date_str + '\nOggetto: ' + subject + '\nUID: ' + uid
                    # add message to dict
                    if folder in scraped_emails:
                        scraped_emails[folder].append(dict_value)
                    else:
                        scraped_emails[folder] = [dict_value]
            except: # no e-mails in the current folder
                pass
        self.__save_logs()
        return scraped_emails

    def set_criteria(self, sender, recipient, subject, from_date, to_date):
        criteria = []
        if sender != '':
            criteria.append(f'(FROM "{sender}")')
        if recipient != '':
            criteria.append(f'(TO "{recipient}")')
        if subject != '':
            criteria.append(f'(SUBJECT "{subject}")')

        criteria.append(f'(SINCE {from_date.strftime("%d-%b-%Y")} BEFORE {to_date.strftime("%d-%b-%Y")})')

        # combine the search criteria
        params = ' '.join(criteria)
        return params
    def write_emails(self, email_id, mail_dir, folder_stripped, folder):
        # Create mail folder
        folder_dir = os.path.join(mail_dir, folder_stripped)
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)
        self.mailbox.select(folder,readonly=True)
        try:
            status, raw_email = self.mailbox.fetch(email_id, "(RFC822)")
        except Exception as e:
            print(e)
        message_mail = raw_email[0][1]

        message = pyzmail.PyzMessage.factory(message_mail)
        sanitized_id = re.sub(r'[<>:"/\\|?*]', '', message.get('message-id')[1:-8])
        filename = f"{sanitized_id}.eml"
        email_path = os.path.join(folder_dir, filename)

        with open(email_path, 'wb') as f:
            f.write(message.as_bytes())
        self.__save_logs()

    def __save_logs(self):
        logs_buffer = io.StringIO()
        original_stderr = sys.stderr
        sys.stderr = logs_buffer
        self.mailbox.print_log()
        self.logs = self.logs + '\n'+logs_buffer.getvalue()
        sys.stderr = original_stderr

    def write_logs(self, acquisition_folder):
        with open(os.path.join(acquisition_folder,'imap_logs.log'),'w') as f:
            f.write(self.logs)

    def download_single_messages(self, mail_dir, emails_dict):
        for folder, emails_list in emails_dict.items():

            for emails in emails_list:
                email_id = emails.partition('UID: ')[2]

                # Create acquisition folder
                folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
                self.write_emails(email_id, mail_dir, folder_stripped)
        self.__save_logs()

    def download_everything(self, project_folder):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in self.mailbox.list()[1]:
            name = folder.decode().split(' "/" ')
            folders.append(name[1])

        # Scrape every message from the folders
        try:
            self.download_messages(folders, project_folder)
        except Exception as e:  # handle exception
                raise Exception(e)
        self.__save_logs()

    def download_messages(self, folders, project_folder):
        for folder in folders:
            folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
            try:
                self.mailbox.select(folder,readonly=True)
                type, data = self.mailbox.search(None, 'ALL')

                # Fetch every message in specified folder
                messages = data[0].split()
                for email_id in messages:
                    self.write_emails(email_id, project_folder, folder_stripped)
            except Exception as e:  # handle exception
                raise Exception(e)
        self.__save_logs()
