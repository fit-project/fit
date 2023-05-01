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

import requests
from configparser import SafeConfigParser
from bs4 import BeautifulSoup

class Authority():
    def __init__(self, temp_x509):
        self.x509_file_path = temp_x509
        parser = SafeConfigParser()
        parser.read('assets/config.ini')
        self.url = parser.get('fit_properties', 'pec_providers_url')
    
    def get_authority(self):
        authority = None
        with open(self.x509_file_path, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                word = "Subject: "
                if row.find(word) != -1:
                    if " O = " in row:
                        authority = row.split(" O = ")[1]
                        authority = authority.split(", ")[0]
                    elif " O=" in row:
                        authority = row.split(" O=")[1]
                        authority = authority.split(", ")[0]
        return authority

    def check_if_authority_is_on_agid_list(self, authority):
        page_num = 0
        found = False

        while True:
            response = requests.get(f'{self.url}?page={page_num}')
            soup = BeautifulSoup(response.text, 'html.parser')

            if authority in soup.get_text():
                found = True

          
            next_button = soup.find('a', {'rel': 'next'})
            if next_button is None:
                break
            else:
                page_num += 1

        if not found:
            return -1
        else:
            return True