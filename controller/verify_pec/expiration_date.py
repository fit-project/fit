#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from common.utility import is_cmd, get_platform
from email import policy
from email.parser import BytesParser
from datetime import datetime
import subprocess
import os


class ExpirationDate:
    def verify(self, eml_file_path, pem_file_path, x509_file_path, textdata_file_path):
        result = {}
        openssl = "openssl"
        is_installed_openssl = is_cmd(openssl)

        if is_installed_openssl is False:
            openssl = ".\ext_lib\openssl\{}\openssl".format(get_platform())
        # extract pem certificate from eml
        extract_pem = subprocess.run(
            [
                openssl,
                "smime",
                "-verify",
                "-in",
                eml_file_path,
                "-noverify",
                "-signer",
                pem_file_path,
                "-out",
                textdata_file_path,
            ],
            capture_output=True,
            text=True,
        )

        # Convert pem to x509
        if extract_pem.returncode == 0:
            output = extract_pem.stdout
            os.system(
                "{} x509 -in {} -text > {}".format(
                    openssl, pem_file_path, x509_file_path
                )
            )
            result = self.__check_date(eml_file_path, x509_file_path)
        else:
            raise Exception(extract_pem.stderr)

        return result

    def __check_date(self, eml_file_path, x509_file_path):
        date_s = None

        with open(x509_file_path, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                word = "Not After"
                if row.find(word) != -1:
                    date_s = row

        with open(eml_file_path, "rb") as fp:
            msg = BytesParser(policy=policy.default).parse(fp)

        # expiration date
        if date_s is not None:
            date_s = date_s.split(" : ")[1]
            date_s = date_s.split(" G")[0]
            date_s = datetime.strptime(date_s, "%b %d %I:%S:%M %Y")

        return {
            "expiration_date": date_s,
            "reply_to": msg["Reply-To"],
            "to": msg["To"],
            "subject": msg["Subject"],
            "send_date": msg["Date"],
        }
