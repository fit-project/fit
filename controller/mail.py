#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
import imaplib
import email
import os
import email.message
import re
import pyzmail


class Mail:
    def __init__(self):
        self.email_address = None
        self.password = None
        self.mailbox = None

    def check_server(self, server, port):
        # Connect and log to the mailbox using IMAP server
        self.mailbox = imaplib.IMAP4_SSL(server, int(port))  # imap ssl port
        return

    def check_login(self, email_address, password):
        self.email_address = email_address
        self.password = password
        self.mailbox.login(self.email_address, self.password)
        self.mailbox.select()
        # Clear password after usage
        self.password = ''
        return

    def get_mails_from_every_folder(self, params):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in self.mailbox.list()[1]:
            name = folder.decode().split(' "/" ')
            folders.append(name[1])

        # Scrape every message from the folders
        scraped_emails = self.fetch_messages(folders, params)
        return scraped_emails

    def fetch_messages(self, folders, params=None):
        scraped_emails = {}
        for folder in folders:
            try:
                self.mailbox.select(folder)
                type, data = self.mailbox.search(None, params)

                # Fetch every message in specified folder
                messages = data[0].split()
                for email_id in messages:
                    status, email_data = self.mailbox.fetch(email_id, "(RFC822)")
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
        if len(scraped_emails) == 0:
            return None
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

    def download_single_messages(self, project_folder, emails_dict):
        for folder, emails_list in emails_dict.items():

            for emails in emails_list:
                email_id = emails.partition('UID: ')[2]

                # Create acquisition folder
                folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
                self.write_emails(email_id, project_folder, folder_stripped)

        return

    def download_everything(self, project_folder):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in self.mailbox.list()[1]:
            name = folder.decode().split(' "/" ')
            folders.append(name[1])

        # Scrape every message from the folders
        self.download_messages(folders, project_folder)
        return

    def download_messages(self, folders, project_folder):
        for folder in folders:
            folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
            try:
                self.mailbox.select(folder)
                type, data = self.mailbox.search(None, 'ALL')

                # Fetch every message in specified folder
                messages = data[0].split()
                for email_id in messages:
                    self.write_emails(email_id, project_folder, folder_stripped)
            except Exception as e:  # handle exception
                pass

    def write_emails(self, email_id, project_folder, folder_stripped):

        # Create acquisition folder
        acquisition_dir = os.path.join(project_folder, 'acquisition', folder_stripped)
        if not os.path.exists(acquisition_dir):
            os.makedirs(acquisition_dir)
        status, raw_email = self.mailbox.fetch(email_id, "(RFC822)")

        message_mail = raw_email[0][1]

        message = pyzmail.PyzMessage.factory(message_mail)

        filename = f"{message.get('message-id')[1:-8]}.eml"
        email_path = os.path.join(project_folder, 'acquisition', folder_stripped, filename)
        with open(email_path, 'wb') as f:
            f.write(message.as_bytes())
        return