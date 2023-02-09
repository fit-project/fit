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
from common.provider import Provider


class Mail:
    def __init__(self, email_address, password):
        self.email_address = email_address
        # TODO: implement secure password handling
        self.password = password



    def check_login(self):
        # Connect and log to the mailbox using IMAP
        provider = Provider()
        server = provider.get_server_from_provider(self.email_address)
        mailbox = imaplib.IMAP4_SSL(server, 993) #imap ssl port
        mailbox.login(self.email_address, self.password)
        mailbox.select()
        # Clear password after usage
        self.password = ''
        return mailbox


    def get_mails_from_every_folder(self, mailbox, project_folder):

        # Retrieve every folder from the mailbox
        folders = []
        for folder in mailbox.list()[1]:
            name = folder.decode().split(' "/" ')
            folders.append(name[1])

        # Scrape every message from the folders
        self.download_messages(mailbox, folders, project_folder)
        mailbox.close()
        mailbox.logout()
        return

    def download_messages(self, mailbox, folders, project_folder):
        for folder in folders:
            folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
            try:
                mailbox.select(folder)
                type, data = mailbox.search(None, 'ALL')
                # Create acquisition folder
                if not os.path.exists(project_folder + '//' + folder_stripped):
                    os.makedirs(project_folder + '//emails//' + folder_stripped)
                # Fetch every message in specified folder
                messages = data[0].split()
                for email_id in messages:
                    status, email_data = mailbox.fetch(email_id, "(RFC822)")
                    email_message = email_data[0][1].decode("utf-8")
                    email_part = email.message_from_bytes(email_data[0][1])
                    acquisition_dir = project_folder + '//emails//' + folder_stripped + '/'
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
                            if (encoding is None):
                                with open(project_folder + '//emails//'+ folder_stripped + '/' +email_id.decode("utf-8") + '/' + filename, 'wb')as f:
                                    f.write(part.get_payload(decode=True))
                                    f.close()
                            else:
                                with open(project_folder + '//emails//'+ folder_stripped + '/' +email_id.decode("utf-8") + '/' + filename.decode(encoding), 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                    f.close()


            except Exception as e: #handle exception
                pass

        return

