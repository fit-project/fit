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

from email.header import decode_header


class Mail:
    def __init__(self):
        self.email_address = None
        # TODO: implement secure password handling
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

    def get_mails_from_every_folder(self, project_folder, params=None):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in self.mailbox.list()[1]:
            name = folder.decode().split(' "/" ')
            folders.append(name[1])

        # Scrape every message from the folders
        for folder in folders:
            folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
            try:
                self.mailbox.select(folder)
                self.download_messages(project_folder, folder_stripped, params)
            except Exception as e:
                pass  # handle exception

        self.mailbox.close()
        self.mailbox.logout()
        return

    def download_messages(self, project_folder, folder_stripped, params=None):
        # Create acquisition folder
        acquisition_folder = os.path.join(project_folder, 'acquisition')
        if not os.path.exists(acquisition_folder):
            os.makedirs(acquisition_folder)

        mailbox_folder = os.path.join(acquisition_folder, folder_stripped)

        # search for every email
        if params is None:
            result, data = self.mailbox.search(None, 'ALL')
        else:
            result, data = self.mailbox.search(None, params)

        if len(data[0]) > 0:
            if not os.path.exists(mailbox_folder):
                os.makedirs(mailbox_folder)
            # Fetch every message in specified folder
            messages = data[0].split()
            for email_id in messages:
                status, email_data = self.mailbox.fetch(email_id, "(RFC822)")
                email_message = email_data[0][1].decode("utf-8")
                email_part = email.message_from_bytes(email_data[0][1])
                acquisition_dir = mailbox_folder + '/'
                with open(
                        '%s/%s.eml' % (acquisition_dir, email_id.decode("utf-8")),
                        'w') as f:
                    f.write(email_message)
                    f.close()

                # attachments acquisition
                for part in email_part.walk():
                    if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                        filename, encoding = decode_header(part.get_filename())[0]
                        path = os.path.join(acquisition_dir, email_id.decode("utf-8"))
                        os.makedirs(path)
                        if encoding is None:
                            with open(mailbox_folder + '/' + email_id.decode(
                                    "utf-8") + '/' + str(filename), 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()
                        else:
                            with open(mailbox_folder + '/' + email_id.decode(
                                    "utf-8") + '/' + filename.decode(encoding), 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()

        return

    def set_criteria(self, project_folder, sender=None, subject=None, from_date=None, to_date=None):
        if sender is None and subject is None and from_date is None and to_date is None:
            self.get_mails_from_every_folder(project_folder)

        else:
            criteria = []
            if sender is not None:
                criteria.append(f'(FROM "{sender}")')
            if subject is not None:
                criteria.append(f'(SUBJECT "{subject}")')
            if (from_date is not None) and (to_date is not None):
                criteria.append(f'(SINCE {from_date.strftime("%d-%b-%Y")} BEFORE {to_date.strftime("%d-%b-%Y")})')

            # combine the search criteria
            params = ' '.join(criteria)
            self.get_mails_from_every_folder(project_folder, params)
        return
