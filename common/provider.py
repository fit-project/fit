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
class Provider:
    def __init__(self):
        self.server = None

    def get_server_from_provider(self, email_address):
        provider = ((email_address.partition('@')[2]).partition('.')[0]).lower()

        # domain = provider.partition('.')[2]
        if provider == 'gmail':
            self.server = 'imap.gmail.com'

        elif provider == 'outlook':
            self.server = 'outlook.office365.com'

        elif provider in ('live', 'hotmail'):  # check the server
            self.server = 'imap-mail.outlook.com'

        elif provider == 'yahoo':
            self.server = '	imap.mail.yahoo.com'

        else:
            # set error
            self.server = None

        return self.server
