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
import re
import email.message


class Mail:
    def __init__(self, email_address, password,project_folder):
        self.email_address = email_address
        # TODO: implement secure password handling
        self.password = password
        self.project_folder = project_folder

    def get_mails_from_every_folder(self):
        server, port = self.set_parameters()

        # Connect and log to the mailbox using IMAP
        mailbox = imaplib.IMAP4_SSL(server, port)
        mailbox.login(self.email_address, self.password)
        # Clear password after usage
        self.password = ''

        # Select messages from Inbox folder
        folders = ['Inbox', 'Sent', 'Drafts', 'Deleted']
        #self.download_messages(mailbox, 'Inbox')
        #self.download_messages(mailbox, 'Sent')
        #self.download_messages(mailbox, 'Draft') #??? check docs
        # self.download_messages(mailbox, 'Trashbin') #??? check docs
        # self.download_messages(mailbox, 'Spam') #??? check docs
        return

    def download_messages(self,mailbox, folder):
        mailbox.select(folder)
        type, data = mailbox.search(None, 'ALL')
        # Create acquisition folder
        if not os.path.exists(self.project_folder + '//' +folder):
            os.makedirs(self.project_folder + '//emails//' +folder)
        # Fetch every message in specified folder

        messages = data[0].split()

        for email_id in messages:
            status, email_data = mailbox.fetch(email_id, "(RFC822)")
            email_data = email_data[0][1].decode("utf-8")

            with open('%s/%s.eml' % (self.project_folder + '//emails//' + folder + '/', email_id.decode("utf-8")), 'w') as f:
                f.write(email_data)
                f.close()

        return

    # TODO: define different servers based on providers
    def set_parameters(self):
        provider = (self.email_address.partition('@')[2]).partition('.')[0]
        #domain = provider.partition('.')[2]
        if provider.lower() == 'gmail':
            server = 'imap.gmail.com'
            port = 993
        elif provider.lower() == 'outlook':
            server = 'outlook.office365.com'
            port = 993
        elif provider.lower() in ('live', 'hotmail'):  # check the server
            server = 'imap-mail.outlook.com'
            port = 993
        else:
            # change this into proper configuration based on provider
            server = 'outlook.office365.com'
            port = 993

        return server, port



